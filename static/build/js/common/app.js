(function() {
  'use strict';

  /* Declare app level module which depends on filters, and services */
  var app, app_name;

  app_name = 'soloha';

  app = angular.module(app_name, [app_name + ".controllers", 'ng.django.urls']);

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

  app.controller('Header', [
    '$http', '$scope', '$window', '$document', '$log', 'djangoUrl', function($http, $scope, $window, $document, $log, djangoUrl) {
      var categories;
      categories = djangoUrl.reverse('promotions:categories');
      return $http.post(categories).success(function(categories) {
        return $scope.categories = categories;
      }).error(function() {
        return console.log('An error occurred during submission');
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

  app.controller('Catalogue', ['$http', '$scope', '$window', '$document', '$log', 'djangoUrl', function($http, $scope, $window, $document, $log, djangoUrl) {}]);

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
