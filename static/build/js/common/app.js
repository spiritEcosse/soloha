(function() {
  'use strict';

  /* Declare app level module which depends on filters, and services */


}).call(this);


/* Controllers */

(function() {


}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = 'soloha';

  app = angular.module(app_name, ['ngResource']);

  app.config([
    '$httpProvider', function($httpProvider) {
      $httpProvider.defaults.xsrfCookieName = 'csrftoken';
      $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
      return $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    }
  ]);

  app.factory('Product', [
    '$resource', function($resource) {
      return $resource('/catalogue/crud/product/', {
        'pk': '@pk'
      });
    }
  ]);

  app.controller('Product', [
    '$http', '$scope', '$window', '$document', '$location', 'Product', function($http, $scope, $window, $document, $location, Product) {
      $scope.pk = 2;
      $scope.product = Product.get({
        pk: $scope.pk
      });
      console.log($scope.product.pk);
      $scope.product.$promise.then(function(product) {
        return $scope.product.pk = product.pk;
      });
      return $http.post($location.absUrl()).success(function(data) {
        return console.log(data);
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
