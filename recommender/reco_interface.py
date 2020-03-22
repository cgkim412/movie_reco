import os
import numpy as np
import pandas as pd
from scipy.sparse import dok_matrix
from sklearn.cluster import AgglomerativeClustering
from movies.models import Movie
from .matfac import MatrixFactorization
from .models import Similarity
from .reco_settings import PARAMS_PATH
from sklearn.preprocessing import normalize


class RecoInterface:
    """
    This is the core interface of the recommendation system.
    All machine learning operations must be handled by this interface alone.
    Other parts of the web application should remain completely ignorant of the inner workings of ML algorithms.
    """

    def __init__(self):
        self.mf = MatrixFactorization()
        self.mf.load("final_151k")
        self.mf.verbose = False
        self.tagged_item_ids = np.array(Similarity.objects.values('movie_id').distinct().
                                        order_by('movie_id').values_list('movie_id', flat=True))
        self.all_item_ids = np.arange(1, 9527)
        self.xpc = self._load_xpc(25)
        self.temporal_discount = self._compute_temporal_discount(2010, 0.015)
        self.label_etc = ("미분류",)

    def _load_xpc(self, n_components):
        data = np.load(os.path.join(PARAMS_PATH, "movie_features_pc50.npy"))
        return pd.DataFrame(data, index=self.tagged_item_ids)[np.arange(n_components)]

    def _compute_temporal_discount(self, threshold, decay_rate):
        years = np.array(Movie.objects.order_by(
            'id').values_list('release_year', flat=True))
        return np.clip(years - threshold, None, 0) * decay_rate

    def _encode_ratings(self, ratings_list):
        X = dok_matrix((1, 9526))
        for movie_id, score in ratings_list:
            X[0, movie_id - 1] = score
        return X.tocsr()

    def _count_occurrences(self, array):
        count = {}
        for val in array:
            count[val] = count.get(val, 0) + 1
        return count

    def get_similar_items(self, movie, limit=20):
        return movie.similar_items.all()[:limit].values_list('other_movie__id', flat=True)

    def _predict_ratings(self, R):
        tagged_indices = self.tagged_item_ids - 1
        pred = self.mf.predict_new(
            R, alpha=0.05, lmbda=0.005, n_iter=30, solve=False)  # d=9526
        sim2pref = normalize(R[:, tagged_indices] @
                             self.xpc) @ normalize(self.xpc).T  # d=8048
        pred[tagged_indices] += 0.25 * sim2pref.flatten()
        pred += self.temporal_discount
        return pred

    def _cluster_and_label(self, movie_ids, k=10, linkage='complete', threshold=0.5):
        applicable_ids = sorted(
            list(set(self.tagged_item_ids).intersection(set(movie_ids))))
        xpc = self.xpc.loc[applicable_ids].copy()
        applicable_ids = xpc.index.values

        # Needs more tests on clustering parameters
        agg = AgglomerativeClustering(n_clusters=None, affinity='cosine', linkage=linkage,
                                      distance_threshold=threshold)
        clusters = agg.fit_predict(xpc)
        count = self._count_occurrences(clusters)
        major_clusters = sorted(count.keys(), key=count.get, reverse=True)[:k]

        clustered_items = []
        labeled_reco_list = {}
        for label in major_clusters:
            member_ids = applicable_ids[clusters == label].tolist()
            repr_genres = tuple(self._get_representative_genres(member_ids))
            if not repr_genres:
                continue
            try:
                labeled_reco_list[repr_genres] += member_ids
            except KeyError:
                try:
                    labeled_reco_list[repr_genres[::-1]] += member_ids
                except KeyError:
                    labeled_reco_list[repr_genres] = member_ids
            clustered_items += member_ids

        labeled_reco_list[self.label_etc] = list(
            set(movie_ids) - set(clustered_items))
        return labeled_reco_list

    def _get_representative_genres(self, movie_ids):
        genres = Movie.objects.filter(id__in=movie_ids).values_list(
            'genres__genre__name_kr', flat=True)
        count = self._count_occurrences(genres)
        sorted_ratios = {
            k: count[k] / len(movie_ids) for k in sorted(count.keys(), key=count.get, reverse=True)}
        repr_genres = []
        for genre, ratio in sorted_ratios.items():
            if ratio >= 0.66:
                repr_genres.append(genre)
            else:
                break
            if len(repr_genres) >= 2:
                break
        return repr_genres

    def get_recommendation(self, user, limit=100):
        # by default ratings are sorted by score in descending order
        ratings = user.ratings.all()
        R = self._encode_ratings(ratings.values_list("movie__id", "score"))
        rated = set(ratings.values_list('movie__id', flat=True))
        reco_list = []

        # recommendation by item-item similarity
        user_favorites = ratings.filter(score__gte=4.0)[:15]
        for fav in user_favorites:
            similar_items = np.random.choice(self.get_similar_items(fav.movie, 20),
                                             size=min(30//len(user_favorites), 10),
                                             replace=False)
            reco_list += similar_items.tolist()

        reco_list = set(reco_list) - rated

        # recommendation by CF
        cf_prediction = self._predict_ratings(R)
        # +1 because DB ids start from 1
        cf_best_items = cf_prediction.argsort(
        )[::-1][:limit + ratings.count()] + 1

        # fill up to limit
        for item in cf_best_items:
            if item not in rated:
                reco_list.add(item)
                if len(reco_list) >= limit:
                    break

        # perform clustering and put labels
        clustered_list = self._cluster_and_label(
            reco_list, k=10, linkage='complete', threshold=0.5)

        # partially re-cluster with relaxed constraints if too many items are labels as "미분류"
        if len(clustered_list[self.label_etc]) > 20:
            clustered_list = self._partial_reclustering(
                clustered_list, self.label_etc, linkage='average', threshold=0.5)

        # reorder dictionary
        clustered_list = self._sort_dict_by_len(
            clustered_list, reverse=True, shuffle=True)
        etc = clustered_list[self.label_etc]
        del clustered_list[self.label_etc]
        clustered_list[self.label_etc] = etc

        return clustered_list

    def _sort_dict_by_len(self, dic, reverse=True, shuffle=False):
        new_dict = {}
        for key in sorted(dic.keys(), key=lambda x: len(dic.get(x)), reverse=reverse):
            if shuffle:
                new_dict[key] = np.random.permutation(dic[key])
            else:
                new_dict[key] = dic[key]
        return new_dict

    def _partial_reclustering(self, labeled_items, key, linkage, threshold):
        etcetera = labeled_items[key]
        clustered_items = labeled_items.copy()
        reclustered = self._cluster_and_label(
            etcetera, linkage=linkage, threshold=threshold)
        del reclustered[key]
        moved_items = []
        for label, items in reclustered.items():
            try:
                clustered_items[label] += items
            except KeyError:
                try:
                    clustered_items[label[::-1]] += items
                except KeyError:
                    if len(items) > 3:
                        clustered_items[label] = items
                        moved_items += items
                        # print(f'{label} 카테고리 새로 생성하여 아이템 {len(items)}개 이동')
                else:
                    # print(f'{label[::-1]} 카테고리로 아이템 {len(items)}개 이동')
                    moved_items += items
            else:
                # print(f'{label} 카테고리로 아이템 {len(items)}개 이동')
                moved_items += items
        clustered_items[key] = list(set(etcetera) - set(moved_items))
        return clustered_items

    def get_eval_list(self, user, limit=100):
        rated_movies = user.ratings.values_list('movie', flat=True)

        # simply return the id of the movies
        eval_candidates = Movie.objects.filter(imdb_votes__gte=3*10**5).filter(imdb_score__gte=6.0).\
            filter(imdb_score__lte=9.0).exclude(
                id__in=rated_movies).values_list('id', flat=True)
        eval_list = np.random.choice(
            eval_candidates, size=limit, replace=False)
        return eval_list

    def save_predictions(self, user, preds):
        pass


RECO_INTERFACE = RecoInterface()
