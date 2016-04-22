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

  app.controller('Product', [
    '$http', '$scope', '$window', '$document', '$location', '$compile', function($http, $scope, $window, $document, $location, $compile) {
      var attributes, product_versions, selected_attributes;
      $scope.product = [];
      $scope.product.values = [];
      $scope.product.attributes = [];
      selected_attributes = [];
      attributes = [];
      product_versions = [];
      $http.post($location.absUrl(), {
        'option_id': $scope.option_id,
        'parent': $scope.parent
      }).success(function(data) {
        $scope.options = data.options;
        $scope.options_children = data.options_children;
        if (data.price) {
          $scope.new_price = data.price;
        } else {
          $scope.product.product_not_availability = data.product_not_availability;
        }
        return console.log(data);
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      $scope.change_price = function() {
        if ($scope.option_model) {
          console.log($scope.options_children[$scope.option_id]);
          if ($scope.options_children[$scope.option_id]) {
            $scope.option_id = Object.keys($scope.options_children[$scope.option_id]).filter(function(key) {
              return $scope.options_children[$scope.option_id][key] === $scope.option_model[$scope.option_id];
            })[0];
          }
        } else {
          $scope.option_id = $scope.confirmed;
        }
        if ($scope.options[$scope.option_id]) {
          $scope.new_price += parseFloat($scope.options[$scope.option_id]);
        } else {
          $scope.parent = true;
        }
        return $http.post($location.absUrl(), {
          'option_id': $scope.option_id,
          'parent': $scope.parent
        }).success(function(data) {
          $scope.options = data.options;
          console.log($scope.options);
          if (Object.keys(data.options_children).length !== 0) {
            $scope.options_children[$scope.option_id] = data.options_children;
            return angular.element(document.getElementById('options-0')).append($compile('<span id="' + $scope.option_id + '"> <select class="form-control" ng-model="option_model[' + $scope.option_id + ']" ng-change="change_price()" ng-options="option for option in options_children[' + $scope.option_id + ']" ></select> </span>')($scope));
          } else {
            return angular.element(document.getElementById('options-0')).append($compile('<div id="' + $scope.option_id + '"> <select class="form-control" ng-model="option_model[' + $scope.option_id + ']" ng-change="change_price()" ng-options="option for option in options" ></select> </div>')($scope));
          }
        }).error(function() {
          return console.error('An error occurred during submission');
        });
      };
      $http.post($location.absUrl()).success(function(data) {
        if (data.price) {
          $scope.product.price = data.price;
        } else {
          $scope.product.product_not_availability = data.product_not_availability;
        }
        product_versions = data.product_versions;
        return angular.forEach(data.attributes, function(attr) {
          var el;
          attributes.push(attr.pk);
          $scope.product.values[attr.pk] = attr.values;
          $scope.product.attributes[attr.pk] = $scope.product.values[attr.pk][0];
          el = angular.element(document).find('#attribute-' + attr.pk);
          el.attr('ng-model', 'product.attributes[' + attr.pk + ']');
          el.attr('ng-options', 'value.title for value in product.values[' + attr.pk + '] track by value.id');
          el.attr('ng-change', 'update_price()');
          return $compile(el)($scope);
        });
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      return $scope.update_price = function() {
        selected_attributes = [];
        angular.forEach(attributes, function(key) {
          return selected_attributes.push($scope.product.attributes[key].id);
        });
        return $scope.product.price = product_versions[selected_attributes.toString()];
      };
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
