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
      var attributes, clone_data, product_versions, selected_attributes;
      $scope.product = [];
      $scope.product.values = [];
      $scope.product.attributes = [];
      selected_attributes = [];
      attributes = [];
      product_versions = [];
      clone_data = null;
      $http.post($location.absUrl()).success(function(data) {
        clone_data = data;
        if (data.price) {
          $scope.product.price = data.price;
        } else {
          $scope.product.product_not_availability = data.product_not_availability;
        }
        product_versions = data.product_versions;
        return angular.forEach(data.attributes, function(attr) {
          var el;
          attributes.push(attr.id);
          $scope.product.values[attr.id] = attr.values;
          $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0];
          if (data.product_version_attributes[attr.id]) {
            $scope.product.attributes[attr.id] = data.product_version_attributes[attr.id];
          }
          el = angular.element(document).find('#attribute-' + attr.id);
          el.attr('ng-model', 'product.attributes[' + attr.id + ']');
          el.attr('ng-options', 'value.title group by value.group for value in product.values[' + attr.id + '] track by value.id');
          el.attr('ng-change', 'update_price(' + attr.id + ')');
          el.attr('attr-dis', '1');
          return $compile(el)($scope);
        });
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      return $scope.update_price = function(attr_id) {
        var el;
        el = angular.element(document).find('#attribute-' + attr_id);
        if (el.attr('attr-dis') === '1') {
          selected_attributes = [];
          angular.forEach(attributes, function(key) {
            if ($scope.product.attributes[key].id !== 0) {
              return selected_attributes.push($scope.product.attributes[key].id);
            }
          });
          if (product_versions[selected_attributes.toString()]) {
            return $scope.product.price = product_versions[selected_attributes.toString()];
          } else {
            angular.forEach(clone_data.variant_attributes[$scope.product.attributes[attr_id].id], function(attr) {
              el = angular.element(document).find('#attribute-' + attr.id);
              el.attr('attr-dis', '0');
              $compile(el)($scope);
              $scope.product.values[attr.id] = attr.values;
              if (attr.in_group[1] && attr.in_group[1].first_visible) {
                return $scope.product.attributes[attr.id] = attr.in_group[1];
              } else if ($scope.product.values[attr.id]) {
                return $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0];
              }
            });
            angular.forEach(attributes, function(key) {
              el = angular.element(document).find('#attribute-' + key);
              el.attr('attr-dis', '1');
              return $compile(el)($scope);
            });
            selected_attributes = [];
            angular.forEach(attributes, function(key) {
              if ($scope.product.attributes[key].id !== 0) {
                return selected_attributes.push($scope.product.attributes[key].id);
              }
            });
            if (product_versions[selected_attributes.toString()]) {
              return $scope.product.price = product_versions[selected_attributes.toString()];
            } else {
              $scope.product.price = clone_data.price;
              return angular.forEach(clone_data.attributes, function(attr) {
                $scope.product.values[attr.id] = attr.values;
                $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0];
                if (clone_data.product_version_attributes[attr.id]) {
                  return $scope.product.attributes[attr.id] = clone_data.product_version_attributes[attr.id];
                }
              });
            }
          }
        }
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
