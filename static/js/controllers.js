var photogallery = angular.module('photogallery', ['ngRoute', 'ngAnimate']);

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

			$http.get("/photos?gallery-id=" + galleryId, {})
			.then(function(data, status, headers, config) {
				var images = data.data;
				if (images.map) {
					images = images.map(function(image) {
						image.src = '/images/' + image.path;
						image.thumbnail = '/thumbnails/' + image.path;
						return image;
					});
				}
			    deferred.resolve(images);
			});

			return deferred.promise;
		},
		galleries: function() {
			var deferred = $q.defer();

			$http.get("/galleries", {})
			.then(function(data, status, headers, config) {
				var galleries = data.data
				if (galleries.map) {
					galleries = galleries.map(function(gallery) {
						gallery.thumbnail = '/thumbnails/' + gallery.thumbnail;
						return gallery;
					})
				}
			    deferred.resolve(data.data);
			});

			return deferred.promise;
		}
	}
}]);

photogallery.directive('slider', function($timeout, $document) {
  return {
    restrict: 'AE',
    replace: true,
    scope: {
      imagespromise: '=',
      currentIndex: '='
    },
    link: function(scope, elem, attrs) {
		scope.images = [];
		 
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

photogallery.controller('GalleryCtrl', ['$scope', 'photodb', '$routeParams', function ($scope, photodb, $routeParams) {
  photodb.photos($routeParams.galleryId).then(function(result) { $scope.images = result; });
  $scope.galleryId = encodeURIComponent(encodeURIComponent($routeParams.galleryId));
}]);

photogallery.controller('GalleryZoomCtrl', ['$scope', 'photodb', '$routeParams', function ($scope, photodb, $routeParams) {
  $scope.images_promise = photodb.photos($routeParams.galleryId);
  $scope.selected_image = $routeParams.selectedIndex;
  $scope.galleryId = $routeParams.galleryId;
}]);


photogallery.controller('GalleryListCtrl', ['$scope', 'photodb', function ($scope, photodb) {
  photodb.galleries().then(function(result) { 
  	$scope.gallery_list = result.map(function(gallery) {
  		gallery.galleryId = gallery.galleryId;
  		return gallery;
  	}); 
  });

  // $scope.gallery_list = [
  // 	{name: 'foo', gallery_dir: encodeURIComponent(encodeURIComponent('static/2013/fotos-erika'))}
  // ];
}]);