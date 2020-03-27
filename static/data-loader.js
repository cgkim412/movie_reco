/*
 *  Written by Changgyu Kim
 *  aneewe@gmail.com
 */


class BaseDataLoader {
    constructor(cardContainerSelector, initBatchSize, batchSize) {
        this.cardContainerSelector = cardContainerSelector;
        this.initBatchSize = initBatchSize;
        this.batchSize = batchSize;
        this._queue = [];
        this._isReady = true;
        this._minDelay = 150; // in millisecond
    }

    initialize(data) {
        this._queue = data;
        this._deploySingleBatchWrapper(this.initBatchSize);
        // Don't bind event listener if queue is already emptied.
        if (this._queue.length > 0) {
            this._setEventListener();
        }
    }

    _eventHandler() {
        if (this._isReady && this._queue.length > 0) {
            // turn off the flag
            this._isReady = false;
            this._deploySingleBatchWrapper(this.batchSize);
            setTimeout(() => {
                this._isReady = true;
            }, this._minDelay);
        }
    }

    _deploySingleBatchWrapper(size = this.batchSize) {
        this._deploySingleBatch(size);
        if (this._queue.length == 0) {
            this._unbindEventListener();
        }
    }

    _setEventListener() {
        // Define the event listener here
        // Make sure to call: this._eventHandler()
    }

    _unbindEventListener() {
        // Unbind the event listener when the job is done
    }

    _deploySingleBatch(size = this.batchSize) {
        // implement this
    }
}

class MovieCardLoaderV extends BaseDataLoader {
    constructor(
        cardContainerSelector,
        initBatchSize = 10,
        batchSize = 5,
        cardClass,
        scrollObject = window
    ) {
        super(cardContainerSelector, initBatchSize, batchSize);
        this._cardClass = cardClass;
        this._scrollOffset = 400;
        this.scrollObject = scrollObject;
    }

    _setEventListener() {
        $(this.scrollObject).scroll(() => {
            if (
                $(document).height() <=
                $(this.scrollObject).scrollTop() + $(this.scrollObject).height() + this._scrollOffset
            ) {
                this._eventHandler();
            }
        });
    }

    _unbindEventListener() {
        $(this.scrollObject).off("scroll");
    }

    _deploySingleBatch(size = this.batchSize) {
        for (let i = 0; i < size && this._queue.length > 0; i++) {
            const movieId = this._queue.shift(); // may use pop() instead
            const card = new this._cardClass(movieId);
            // define the error callback for the card object here
            card.errorCallback = () => {
                this._deploySingleBatch(1);
            };
            card.appendTo(this.cardContainerSelector);
        }
    }
}

class RatedMovieCardLoader extends MovieCardLoaderV {
    constructor(
        cardContainerSelector,
        initBatchSize = 10,
        batchSize = 5,
        cardClass = StarMovieCard
    ) {
        super(cardContainerSelector, initBatchSize, batchSize);
        this._cardClass = cardClass;
        this._scrollOffset = 400;
    }

    _deploySingleBatch(size = this.batchSize) {
        for (let i = 0; i < size && this._queue.length > 0; i++) {
            const rating = this._queue.shift(); // may use pop() instead
            const card = new this._cardClass(rating.movie, rating.score, true);
            // define the error callback here
            card.errorCallback = () => {
                this._deploySingleBatch(1);
            };
            card.appendTo(this.cardContainerSelector);
        }
    }
}

class MovieCardLoaderH extends BaseDataLoader {
    constructor(
        cardContainerSelector,
        initBatchSize = 5,
        batchSize = 3,
        cardClass
    ) {
        super(cardContainerSelector, initBatchSize, batchSize);
        this._cardClass = cardClass;
        this._minDelay = 450;
        this._scrollOffset = 300;
    }

    _setEventListener() {
        $(this.cardContainerSelector)
            .siblings(".arrow-right")
            .on("click", () => {
                this._eventHandler();
            });
    }

    _unbindEventListener() {
        $(this.cardContainerSelector)
            .siblings(".arrow-right")
            .off("click");
    }

    _deploySingleBatch(size = this.batchSize) {
        for (let i = 0; i < size && this._queue.length > 0; i++) {
            const movieId = this._queue.shift(); // may use pop() instead
            const card = new this._cardClass(movieId);
            // define the error callback here
            card.errorCallback = () => {
                this._deploySingleBatch(1);
            };
            card.appendTo(this.cardContainerSelector);
        }
    }
}

class ArrowedCardContainer {
    constructor(id, label, numItems = "") {
        this.id = id;
        this.label = label;
        this.numItems = numItems;
        this.idPrefix = "container-ac-";
        this.selector = "#" + this.idPrefix + this.id;
    }

    renderTemplate() {
        const container = `
    <div class="carousel container-wrapper mt-3" container-id="${this.id}">
      <div class="text-light ml-3 mb-2">
        <span class="h4">${this.label.join(" / ")}</span>
        <span class="h5">(${this.numItems}개)</span>
      </div>
      <span class="carousel-control-prev arrow-left" role="button" style="width: 20px;">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      </span>
      <div id="${this.idPrefix + this.id}" class="card-container d-flex"></div>
      <span class="carousel-control-next arrow-right" role="button" style="width: 20px;">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
      </span>
    </div>
    `;
        return container;
    }
}

class CardContainerLoader extends MovieCardLoaderV {
    constructor(
        parentSelector,
        initBatchSize = 3,
        batchSize = 1,
        containerClass
    ) {
        super(parentSelector, initBatchSize, batchSize, null);
        this.parentSelector = parentSelector; // just for easier reference
        this._indexCount = 0;
        this.containerClass = containerClass;
    }

    _deploySingleBatch(size = this.batchSize) {
        for (let i = 0; i < size && this._queue.length > 0; i++) {
            const containerData = this._queue.shift(); // may use pop() instead
            this._indexCount += 1;
            // create a new container and append it to the DOM
            const container = new this.containerClass(
                this._indexCount,
                containerData.label,
                containerData.items.length
            );
            const containerTemplate = container.renderTemplate();
            $(this.parentSelector).append(containerTemplate);
            // then activate a CardLoader to fill the container
            const loader = new MovieCardLoaderH(
                container.selector,
                8,
                4,
                SimpleMovieCard
            );
            loader.initialize(containerData.items);
        }
    }
}

const eventManager = {
    mainContainerSelector: "#container-main",
    modalContainerSelector: "#container-modal",
    intersectionObserver: null,

    _scrollContainer: function (container, direction) {
        const currentPosition = container.scrollLeft();
        const scrollDirection = direction == "right" ? 1 : -1;
        const scrollDistance = container.width();
        container.scrollLeft(currentPosition + scrollDirection * scrollDistance);
    },

    setupIntersectionObserver: function () {
        const options = {
            root: null,
            rootMargin: "0px",
            threshold: 0.25
        };
        const callback = function (entries, observer) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    $(entry.target)
                        .find(".lazy-load")
                        .removeClass("lazy-load");
                }
            });
        };
        this.intersectionObserver = new IntersectionObserver(callback, options);
    },

    activateArrowedContainers: function () {
        $(this.mainContainerSelector).on("click", ".arrow-left", event => {
            const arrow = $(event.target).parent();
            const cardContainer = $(arrow).siblings(".card-container");
            this._scrollContainer(cardContainer, "left");
            $(arrow).toggleClass("arrow-left");
            setTimeout(() => {
                $(arrow).toggleClass("arrow-left");
            }, 500);
        });
        $(this.mainContainerSelector).on("click", ".arrow-right", event => {
            const arrow = $(event.target).parent();
            const cardContainer = $(arrow).siblings(".card-container");
            this._scrollContainer(cardContainer, "right");
            $(arrow).toggleClass("arrow-right");
            setTimeout(() => {
                $(arrow).toggleClass("arrow-right");
            }, 500);
        });
    },

    activateMovieDetailModals: function () {
        $(this.mainContainerSelector).on(
            "click",
            ".card-container .card-clickable",
            function () {
                const detailCard = new DetailedMovieCard(
                    $(this)
                        .parent()
                        .attr("movie-id")
                );
                detailCard.showAsModal();
            }
        );
        $(this.modalContainerSelector).on(
            "click",
            ".modal .container-sim .card-clickable",
            event => {
                $(this.modalContainerSelector)
                    .find(".modal, show")
                    .modal("hide");
                const detailCard = new DetailedMovieCard(
                    $(event.currentTarget)
                        .parent()
                        .attr("movie-id")
                );
                detailCard.showAsModal();
            }
        );
    },

    activateAll: function () {
        this.activateArrowedContainers();
        this.activateMovieDetailModals();
        if ("IntersectionObserver" in window) {
            this.setupIntersectionObserver();
        } else {
            $("#style-lazy").remove();
        }
    }
};
