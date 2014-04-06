var photogallery = angular.module('photogallery', ['ngRoute', 'ngAnimate', 'infinite-scroll']);

/**
 * Todo:
 * - gallery import should spawn thumbnail generation, but not block on it;
 * - website can work without thumbnails. if thumbnail doesn't exist, then generate it or present dummy thumbnail
 */

photogallery.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/galleries', {
        templateUrl: 'partials/gallery_list.html',
        controller: 'GalleryListCtrl'
      }).
      when('/gallery/:galleryId', {
        templateUrl: 'partials/gallery.html',
        controller: 'GalleryCtrl'
      }).
      when('/gallery-zoom/:galleryId/:selectedIndex', {
        templateUrl: 'partials/gallery-zoom.html',
        controller: 'GalleryZoomCtrl'
      }).
      otherwise({
        redirectTo: '/galleries'
      });
  }]); 


photogallery.factory('photodb', ['$http', '$q', function($http, $q, $scope) {
	return {
		photos: function(galleryId) {
			var deferred = $q.defer();

			$http.get("/galleries/" + galleryId, {})
			.then(function(data, status, headers, config) {
				var images = data.data;
			    deferred.resolve(images);
			});

			return deferred.promise;
		},
		galleries: function() {
			var deferred = $q.defer();

			$http.get("/galleries", {})
			.then(function(data, status, headers, config) {
				var galleries = data.data
			    deferred.resolve(data.data);
			});

			return deferred.promise;
		},
		setFavorite: function(galleryId, imagePath, favorite) {
			$http.post("/galleries/" + galleryId + "/photos/" + imagePath, {
				favorite: favorite
			});
		}
	}
}]);

photogallery.directive('favorite', ['photodb', function(photodb) {
	return {
		restrict: 'AE',
		replace: true,
		template: '<div style="width: 30px;"></div>',
		scope: {
			image: '='
		},
		link: function(scope, elem, attrs, controllerInstance) {
			var setFavoriteClass = function(isFavorite) {
				if (isFavorite) {
					elem.removeClass('favorite-hover');
					elem.addClass('favorite');
					elem.removeClass('non-favorite');
				}
				else {
					elem.removeClass('favorite-hover');
					elem.addClass('non-favorite');
					elem.removeClass('favorite');
				}				
			}

			scope.image.favorite = scope.image.favorite || false;
			setFavoriteClass(scope.image.favorite);

			elem.bind('click', function() {
				// scope.imagespromise.then(function(images) {
				// 	var image = images[scope.currentIndex];
				// 	scope.isFavorite = !scope.isFavorite;
				// 	photodb.setFavorite(image.gallery_id, image.path, scope.isFavorite);
				// })
				scope.image.favorite = ! scope.image.favorite;
				photodb.setFavorite(scope.image.gallery_id, scope.image.path, scope.image.favorite);
				setFavoriteClass(scope.image.favorite);
			});

			elem.bind('mouseover', function() {
				elem.addClass('favorite-hover');
			});

			elem.bind('mouseout', function() {
				elem.removeClass('favorite-hover');
			});
		}
	};
}]);

photogallery.directive('slider', function($timeout, $document, $location) {
  return {
    restrict: 'AE',
    replace: true,
    scope: {
      imagespromise: '=',
      currentIndex: '=',
      isFavorite: '='
    },
    link: function(scope, elem, attrs) {
		scope.images = [];
		scope.currentIndex = parseInt(scope.currentIndex);
		 
		scope.next = function() {
		  scope.currentIndex < scope.numImages - 1 ? scope.currentIndex++ : scope.currentIndex = 0;
		};
		 
		scope.prev = function() {
		  scope.currentIndex > 0 ? scope.currentIndex-- : scope.currentIndex = scope.numImages - 1;
		};    	

		scope.$watch('currentIndex', function() {
		  scope.imagespromise.then(function(images) {
		  	for (i = 0; i < 5; i++) {
			  	scope.images[i] = images[(scope.currentIndex + i - 2 + images.length) % images.length];
			  	scope.images[i].visible = false;
		  	}
		  	scope.images[2].visible = true;
		  	scope.numImages = images.length;
		  });		 
		});

		// var timer;
		// var sliderFunc = function() {
		//   timer = $timeout(function() {
		//     scope.next();
		//     timer = $timeout(sliderFunc, 5000);
		//   }, 5000);
		// };
		 
		// sliderFunc();
		 
		// scope.$on('$destroy', function() {
		//   $timeout.cancel(timer); // when the scope is getting destroyed, cancel the timer
		// });

		$document.bind("keydown", function (event) {
            if(event.which === 37 || event.which === 38) {
                scope.prev();
                scope.$digest()
            }
            if(event.which === 39 || event.which === 40) {
                scope.next();
                scope.$digest()
            }
        });
    },
    templateUrl: 'partials/slider.html'
  };
});

photogallery.controller('GalleryListCtrl', ['$scope', 'photodb', function ($scope, photodb) {
    var galleriesPromise = photodb.galleries();
    var n = 8;
    var firstBatchLoaded = galleriesPromise.then(function(allGalleries) {
        $scope.gallery_list = allGalleries.slice(0, n);
        return allGalleries;
    });
    $scope.loadMore = function() {
        firstBatchLoaded.then(function(allGalleries) { 
            var last = $scope.gallery_list.length;
            for(var i = 0; i < n && last + i < allGalleries.length; i++) {
              $scope.gallery_list.push(allGalleries[last + i]);
            }
        })
    };
}]);

photogallery.controller('GalleryCtrl', ['$scope', 'photodb', '$routeParams', function ($scope, photodb, $routeParams) {
    var galleryId = $routeParams.galleryId;
    var photosPromise = photodb.photos(galleryId);
    var n = 8;
    var firstBatchLoaded = photosPromise.then(function(allImages) {
        $scope.images = allImages.slice(0, n);
        return allImages;
    });
    $scope.loadMore = function() {
        firstBatchLoaded.then(function(allImages) {            
            var last = $scope.images.length;
            for(var i = 0; i < n && last + i < allImages.length; i++) {
              $scope.images.push(allImages[last + i]);
            }
        });
    };
    $scope.galleryId = encodeURIComponent(encodeURIComponent(galleryId));
}]);

photogallery.controller('GalleryZoomCtrl', ['$scope', 'photodb', '$routeParams', function ($scope, photodb, $routeParams) {
  $scope.images_promise = photodb.photos($routeParams.galleryId);
  $scope.selected_image = $routeParams.selectedIndex;
  $scope.gallery_id = $routeParams.galleryId;
}]);


