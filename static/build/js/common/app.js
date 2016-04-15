(function() {
  'use strict';

  /* Declare app level module which depends on filters, and services */
  var app, app_name;

  app_name = 'soloha';

  app = angular.module(app_name, ['ng.django.urls', 'ui.bootstrap']);

  app.config([
    '$httpProvider', '$locationProvider', function($httpProvider, $locationProvider) {
      $httpProvider.defaults.xsrfCookieName = 'csrftoken';
      $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
      $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
      $locationProvider.html5Mode({
        enabled: true,
        requireBase: false
      });
      return $locationProvider.hashPrefix('!');
    }
  ]);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = "soloha";

  app = angular.module(app_name, []);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = "soloha";

  app = angular.module(app_name, []);

  app.controller('Product', [
    '$http', '$scope', '$location', '$window', '$document', '$log', function($http, $scope, $location, $window, $document, $log) {
      var message;
      $scope.product = [];
      $scope.product.price = '12';
      console.log($location.absUrl());
      $http.post('http://127.0.0.1:8000/category-1/category-12/category-123/product-1', message = 'test');
      return $http.post($location.absUrl()).success(function(data) {
        console.log(data);
        $scope.products = data.products;
        return $scope.paginator = data.paginator;
      }).error(function() {
        return console.error('An error occurred during submission');
      });
    }
  ]);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = "soloha";

  app = angular.module("" + app_name + ".controllers", []);

  app.controller('Home', [
    '$http', '$scope', '$window', '$document', '$log', 'djangoUrl', function($http, $scope, $window, $document, $log, djangoUrl) {
      var hits, news, recommends;
      hits = djangoUrl.reverse('promotions:hits');
      recommends = djangoUrl.reverse('promotions:recommend');
      return news = djangoUrl.reverse('promotions:new');
    }
  ]);

}).call(this);
