import os
import numpy as np
import pandas as pd
from scipy.sparse import dok_matrix
from sklearn.cluster import AgglomerativeClustering
from movies.models import Movie
from .matfac import MatrixFactorization
from .models import Similarity
from .reco_settings import PARAMS_PATH


class RecoInterface:
    """
    This is the core interface of the recommendation system.
    All machine learning operations must be handled by this interface alone.
    Other parts of the web application should remain completely ignorant of the inner workings of ML algorithms.
    """

    def __init__(self):
        self.mf = MatrixFactorization()
        self.mf.load_params("matfac_final")
        self.tagged_item_ids = Similarity.objects.values('movie_id').distinct().order_by('movie_id').values_list(
            'movie_id', flat=True)
        self.all_item_ids = np.arange(1, 9527)
        self.xpc = self._load_xpc()

    def _load_xpc(self):
        data = np.load(os.path.join(PARAMS_PATH, "movie_features_pc50.npy"))
        return pd.DataFrame(data, index=self.tagged_item_ids)

    def _encode_ratings(self, ratings_list):
        X = dok_matrix((1, 9526))
        for movie_id, score in ratings_list:
            X[0, movie_id - 1] = score
        return X.tocsr()

    def _predict_ratings(self, R):
        return np.ravel(self.mf.predict_new_hybrid(R))

    def get_similar_items(self, movie, limit=20):
        return movie.similar_items.all()[:limit].values_list('other_movie__id', flat=True)

    def decode_prediction(self, prediction):
        pass

    def _cluster_and_label(self, movie_ids):
        applicable_ids = sorted(list(set(self.tagged_item_ids).intersection(set(movie_ids))))
        xpc = self.xpc.loc[applicable_ids].copy()
        applicable_ids = xpc.index.values

        # Run some test on average vs complete linkages
        agg = AgglomerativeClustering(n_clusters=None, affinity='cosine', linkage='average', distance_threshold=0.5)
        clusters = agg.fit_predict(xpc)

        count = self._count_occurrences(clusters)
        major_clusters = sorted(count.keys(), key=count.get, reverse=True)[:8]

        clustered_items = []
        unlabeled = []
        labeled_reco_list = {}
        for label in major_clusters:
            member_ids = applicable_ids[clusters == label].tolist()
            repr_genres = tuple(self._get_representative_genres(member_ids))
            if not repr_genres:
                unlabeled += member_ids
                continue
            try:
                labeled_reco_list[repr_genres] += member_ids
            except KeyError:
                labeled_reco_list[repr_genres] = member_ids

            clustered_items += member_ids

        labeled_reco_list["기타"] = list(set(movie_ids) - set(clustered_items)) + unlabeled
        return labeled_reco_list

    def _get_representative_genres(self, movie_ids):
        genres = Movie.objects.filter(id__in=movie_ids).values_list('genres__genre__name_kr', flat=True)
        count = self._count_occurrences(genres)
        sorted_ratios = {k: count[k] / len(movie_ids) for k in sorted(count.keys(), key=count.get, reverse=True)}
        repr_genres = []
        for genre, ratio in sorted_ratios.items():
            if ratio >= 0.5:
                repr_genres.append(genre)
            else:
                break
            if len(repr_genres) >= 2:
                break
        return repr_genres

    def _count_occurrences(self, array):
        count = {}
        for val in array:
            count[val] = count.get(val, 0) + 1
        return count

    def get_recommendation(self, user, limit=100):
        ratings = user.ratings.all() # by default ratings are sorted by score in descending order
        R = self._encode_ratings(ratings.values_list("id", "score"))

        # recommendation by CF
        cf_prediction = self._predict_ratings(R)
        cf_best_items = (-cf_prediction).argsort()[:limit + ratings.count()] + 1 # +1 because DB ids start from 1

        reco_list = set(cf_best_items)

        # recommendation by item similarity
        user_favorites = ratings.filter(score__gte=3.5)[:3]
        for fav in user_favorites:
            similar_items = self.get_similar_items(fav.movie, 10)
            for item in similar_items:
                reco_list.add(item)

        # remove items that are already rated by the user
        reco_list = list(reco_list - set(ratings.values_list('id', flat=True)))[:limit]

        # perform clustering and put labels
        clustered_list = self._cluster_and_label(reco_list)

        return clustered_list

    def get_eval_list(self, user, limit=100):
        rated_movies = user.ratings.values_list('movie', flat=True)

        # simply return the id of the movies
        eval_candidates = Movie.objects.filter(imdb_votes__gte=10**5).filter(imdb_score__gte=6.0).\
            filter(imdb_score__lte=8.0).exclude(id__in=rated_movies).values_list('id', flat=True)
        eval_list = np.random.choice(eval_candidates, size=limit, replace=False)
        return eval_list

    def save_predictions(self, user, preds):
        pass


RECO_INTERFACE = RecoInterface()
