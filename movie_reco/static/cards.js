/*
 *  Written by Changgyu Kim
 *  aneewe@gmail.com
 */

// assumes following variables are defined in the global scope
// movieBaseUrl, evalBaseUrl, csrftoken, eventManager

class BaseMovieCard {
    constructor(movieId) {
        this.movieId = movieId
        this.dataUrl = movieBaseUrl + movieId + '/lite/'
        this.cardId = 'movie-card-' + movieId
        this.parentSelector = null
    }

    _getMovieData() {
        $.ajax({
            url: this.dataUrl,
            method: 'GET',
            dataType: 'json',
            success: response => {
                this._successCallback(JSON.parse(response))
            },
            error: response => {
                this.errorCallback(response)
            }
        })
    }

    _successCallback(data) {
        // override this
        const html = this._renderTemplate(data)
        $(this.parentSelector).append(html)
    }

    errorCallback(response) {
        // override this (optional)
    }

    _renderTemplate() {
        // override this
    }

    appendTo(parentSelector) {
        this.parentSelector = parentSelector
        this._getMovieData()
    }
}

class StarMovieCard extends BaseMovieCard {
    constructor(movieId, initScore = 0, useAltColors = false) {
        super(movieId)
        this.ratingId = 'rating-' + movieId
        this.initScore = initScore
        this.useAltColors = useAltColors
        this.cardId = 'movie-card-star' + movieId
    }

    _successCallback(data) {
        super._successCallback(data)
        ratingManager.applyStarRating(
            this.movieId,
            this.initScore,
            this.useAltColors
        )
    }

    _renderTemplate(movie) {
        const card = `<div class="col-6 col-md-4 col-lg-3 px-0 mx-0">
            <div id="${this.cardId}" class="card h-100 mb-1 border-black text-white bg-dark">
                <div class="card-header border-dark" style="background: url(${movie.poster}); background-position: center center;
                background-size: contain; background-repeat: no-repeat; min-height: 250px; max-height:400px;"></div>
                <div class="card-body my-1 py-1 my-md-2 text-center">
                    <h6 class="card-title mb-0">${movie.title_kr} (${movie.release_year})</h6>
                </div>
                <div class="text-center mt-0 mb-3" id="${this.ratingId}"></div>
            </div></div>`
        return card
    }
}

class MoviePosterCard extends BaseMovieCard {
    constructor(movieId) {
        super(movieId)
        this.cardId = 'movie-card-poster' + movieId
    }

    _renderTemplate(movie) {
        const card = `<div class="col-4 col-lg-3 px-0 mx-0 my-0 my-lg-1">
            <div id="${this.cardId}" class="card h-100 my-0 mx-1 mx-md-2 mx-lg-3 bg-dark text-light" movie-id="${movie.id}">
                <div class="card-header card-clickable h-100 movie-poster border-dark" style="background: url(${movie.poster}); background-position: center center;
                background-size: contain; background-repeat: no-repeat; min-height: 150px;"></div>
            </div></div>`
        return card
    }
}

class SimpleMovieCard extends BaseMovieCard {
    constructor(movieId) {
        super(movieId)
        this.cardId = 'movie-card-simple-' + movieId
    }
    _renderTemplate(movie) {
        const card = `<div class="col-4 col-lg-3 px-0 mx-0">
            <div id="${this.cardId}" class="card h-100 mx-0 my-0 bg-dark text-light" movie-id="${movie.id}">
                <div class="lazy-load card-header card-clickable h-100 mx-1 mx-md-2 mx-lg-3 border-dark" style="background: url(${movie.poster}); background-position: center center;
                background-size: contain; background-repeat: no-repeat; min-height: 160px;"></div>
                <div class="card-body mx-auto my-auto px-0 pt-0 pb-1 text-center" style="min-height: 60px;">
                <p class="h6 card-title mb-0">${movie.title_kr} (${movie.release_year})</p></div>
            </div></div>`
        return card
    }

    _successCallback(data) {
        // testing the lazy loading functionality
        const html = this._renderTemplate(data)
        $(this.parentSelector).append(html)

        if (eventManager.intersectionObserver) {
            const target = $('#' + this.cardId)[0]
            eventManager.intersectionObserver.observe(target)
        }
    }
}

class DetailedMovieCard extends BaseMovieCard {
    constructor(movieId) {
        super(movieId)
        this.cardId = 'movie-card-detail-' + movieId
        this.modalSelector = '#modal-' + movieId
        this.dataUrl = movieBaseUrl + movieId + '/'
        this.modalContainerSelector = '#container-modal'
        this._similarItems = null
        this._simContainerId = 'container-sim-' + movieId
    }

    _renderTemplate(movie) {
        const slicePosition = 250
        const overviewVisible = movie.overview.slice(0, slicePosition)
        const overviewHidden = movie.overview.slice(slicePosition)
        let readMore = null
        if (movie.overview.length > slicePosition) {
            readMore = `<span class="overview-toggle">...<button class="btn btn-sm mt-1 btn-outline-light read-more">더 보기</button></span>`
        } else {
            readMore = ''
        }
        const simContainer = this._renderSimContainerDiv(movie)
        const card = `<div id="${this.cardId}" class="card bg-dark text-light">
            <div class="card-header px-0 py-0 border-dark" style="background: url(${
            movie.poster
            }); background-position: center center;
                background-size: cover; height: 25vh;">
            </div>
            <div class="card-body pb-0">
                <span class="text-center">
                    <h4 class="card-title">${movie.title_kr}</h4>
                    <h5 class="card-subtitle mb-3">(${movie.title}, ${
            movie.release_year
            })</h5>
                </span>
                <p class="mb-1">장르:  ${movie.genres.join(', ')}</p>
                <p class="mb-1">상영시간: ${movie.runtime}분</p>
                <p class="mb-1">국가: ${movie.countries.join(', ')}</p>
                <p class="mb-1">출연: ${movie.actors.join(', ')}</p>
                <p class="mb-1">감독: ${movie.directors.join(', ')}</p>
                <p>평점: ${Math.round(
                movie.imdb_score * 10
            )}% (IMDB)<span class="mx-2">||</span> ${Math.round(
                movie.tmdb_score * 10
            )}% (TMDB)</p>

            </div>
            <div class="card-body overview">
                <h6 class="ml-1 mb-1">줄거리</h6>
                <p><small>
                    ${overviewVisible}${readMore}<span class="overview-toggle d-none">${overviewHidden}</span>
                </small></p>
            </div>
            ${simContainer}
            <div class="card-footer mt-0 pt-0 bg-dark border-dark">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span class="text-light my-0 h1" aria-hidden="true">&times;</span>
                </button>
            </div></div>`
        return card
    }

    _renderSimContainerDiv(data) {
        let html = null
        if (data.similar_items.length > 0) {
            html = `<div class="card-body text-center mx-0 px-0">
                <button class="btn btn-outline-warning show-similar-items mb-2" type="button"
                    data-toggle="collapse" data-target="#${this._simContainerId}">
                    비슷한 영화 보기
                </button>
                <div id="${this._simContainerId}" class="container-sim row collapse mx-0 px-0"></div></div>`
        } else {
            html = ''
        }
        return html
    }

    showAsModal() {
        if ($(this.modalContainerSelector).find(this.modalSelector).length == 0) {
            this._getMovieData()
        } else {
            $(this.modalSelector).modal('show')
        }
    }

    _setEventListener() {
        $(this.modalSelector)
            .find('.read-more')
            .on('click', function (event) {
                $(event.target)
                    .parent()
                    .parent()
                    .find('.overview-toggle')
                    .toggleClass('d-none')
            })

        $(this.modalSelector).on('hide.bs.modal', function (event) {
            $(event.target)
                .find('.overview-toggle')
                .toggleClass('d-none')
            $(event.target)
                .find('.container-sim')
                .collapse('hide')
        })

        if (this._similarItems.length > 0) {
            $(this.modalSelector)
                .find('.show-similar-items')
                .on('click', () => {
                    const simContainerSelector = '#' + this._simContainerId
                    if ($(simContainerSelector).children().length == 0) {
                        const loader = new MovieCardLoaderV(
                            simContainerSelector,
                            12,
                            0,
                            MoviePosterCard,
                            null
                        )
                        loader.initialize(this._similarItems)
                    } else {
                        $(this.modalSelector)
                            .find('.show-similar-items')
                            .off('click')
                    }
                })
        }
    }

    _successCallback(data) {
        this._similarItems = data.similar_items
        const html = this._renderAsModal(data)
        $(this.modalContainerSelector).append(html)
        this._setEventListener()
        $(this.modalSelector).modal('show')
    }

    _renderAsModal(data) {
        const card = this._renderTemplate(data)
        const modal = `<div id="modal-${data.id}" class="modal">
            <div class="modal-dialog modal-dialog-centered modal-lg" role="document">
                <div class="modal-content">${card}</div>
            </div></div>`
        return modal
    }
}

const ratingManager = {
    _selectorPrefix: '#rating-',
    _ratingCountSelector: '#rating-count',
    _updateRatingCount: function (newCount) {
        $(this._ratingCountSelector).text(newCount)
        if (newCount >= 10) {
            $('#ready-note').removeClass('d-none')
        }
    },
    _submitRating: function (movieId, rating) {
        const method = rating == 0 ? 'DELETE' : 'POST'
        $.ajax({
            headers: { 'X-CSRFToken': csrftoken },
            method: method,
            url: evalBaseUrl + movieId + '/',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({ score: rating }),
            processData: true,
            dataType: 'json',
            success: response => {
                this._updateRatingCount(JSON.parse(response).rating_count)
            }
        })
    },
    applyStarRating: function (movieId, initScore, useAltColors) {
        const selector = this._selectorPrefix + movieId
        const color1 = useAltColors == true ? 'coral' : 'gold'
        const color2 = useAltColors == true ? 'tomato' : 'orange'
        $(selector).starRating({
            initialRating: initScore,
            hoverColor: color1,
            starGradient: { start: color1, end: color2 },
            callback: (rating, $el) => {
                this._submitRating(movieId, rating)
            }
        })
    }
}
