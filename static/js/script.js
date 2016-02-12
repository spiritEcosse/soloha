(function() {
  'use strict';

  /* Declare app level module which depends on filters, and services */
  var app, app_name;

  app_name = 'promotions';

  app = angular.module(app_name, [app_name + ".controllers", 'ui.bootstrap', 'ngAnimate', 'duScroll']);

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

  app_name = "catalog";

  app = angular.module(app_name + ".controllers", []);

  app.controller('Product', [
    '$http', '$scope', '$window', '$document', function($http, $scope, $window, $document) {
      var alerts, duration, offset;
      $scope.alerts = [];
      $scope.quantity = 1;
      duration = 800;
      offset = 100;
      alerts = angular.element(document.getElementById('alerts'));
      $scope.closeAlert = function(index) {
        return $scope.alerts.splice(index, 1);
      };
      return $scope.add_to_cart = function() {
        $scope.disabled = true;
        if ($scope.quantity < 1) {
          return false;
        }
        $http.post('/catalog/product_add_to_cart/' + $scope.product.pk + '/', {
          quantity: $scope.quantity
        }).success(function(data) {
          $scope.alerts.unshift({
            msg: data.msg,
            type: 'success'
          });
          $document.scrollToElement(alerts, offset, duration);
          return $scope.disabled = false;
        }).error(function() {
          return console.error('An error occurred during submission');
        });
        return false;
      };
    }
  ]);

  app.directive('alertSuccess', ['$scope', function($scope) {}]);

}).call(this);
