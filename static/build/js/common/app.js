(function() {
  'use strict';

  /* Declare app level module which depends on filters, and services */
  var app, app_name;

  app_name = 'soloha';

  app = angular.module(app_name, [app_name + ".controllers", 'ng.django.urls', 'ui.bootstrap']);

  app.config([
    '$httpProvider', function($httpProvider) {
      $httpProvider.defaults.xsrfCookieName = 'csrftoken';
      $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
      return $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    }
  ]);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = "soloha";

  app = angular.module(app_name + ".controllers", []);

  app.factory('superCache', [
    '$cacheFactory', function($cacheFactory) {
      return $cacheFactory('super-cache');
    }
  ]);

  app.controller('Header', [
    '$http', '$scope', '$location', '$window', '$document', '$log', '$cacheFactory', 'djangoUrl', function($http, $scope, $location, $window, $document, $log, $cacheFactory, djangoUrl) {
      var cache, categories;
      categories = djangoUrl.reverse('promotions:categories');
      cache = $cacheFactory('superCache');
      if (!cache.get("categories")) {
        return $http.post(categories, {
          cache: true
        }).success(function(categories) {
          $scope.categories = categories;
          console.log('not in cache');
          return cache.put("categories", categories);
        }).error(function() {
          return console.log('An error occurred during submission');
        });
      } else {
        return $scope.categories = cache.get("categories");
      }
    }
  ]);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = "soloha";

  app = angular.module(app_name + ".controllers");

  app.controller('Catalogue', [
    '$http', '$scope', '$location', '$window', '$document', '$log', 'djangoUrl', function($http, $scope, $location, $window, $document, $log, djangoUrl) {
      var products_url;
      products_url = djangoUrl.reverse('catalogue:products');
      return $scope.$watch("category", function() {
        return $http.post(products_url, {
          category_pk: $scope.category.pk
        }).success(function(data) {
          $scope.products = data.products;
          return $scope.paginator = data.paginator;
        }).error(function() {
          return console.error('An error occurred during submission');
        });
      });
    }
  ]);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = "soloha";

  app = angular.module(app_name + ".controllers");

  app.controller('Home', [
    '$http', '$scope', '$window', '$document', '$log', 'djangoUrl', function($http, $scope, $window, $document, $log, djangoUrl) {
      var hits, news, recommends;
      hits = djangoUrl.reverse('promotions:hits');
      recommends = djangoUrl.reverse('promotions:recommend');
      news = djangoUrl.reverse('promotions:new');
      $http.post(news).success(function(products) {
        $scope.products = products;
        return $scope.news = products;
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      $http.post(recommends).success(function(products) {
        return $scope.recommends = products;
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      $scope.get_news = function() {
        return $scope.products = $scope.news;
      };
      $scope.get_recommends = function() {
        return $scope.products = $scope.recommends;
      };
      $scope.get_special = function() {
        return $scope.products = [];
      };
      return $scope.get_hits = function() {
        return $scope.products = [];
      };
    }
  ]);

}).call(this);
