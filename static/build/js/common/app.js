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
      var attributes, clone_data, prefix, selector_el, set_price;
      $scope.product = [];
      $scope.product.values = [];
      $scope.product.attributes = [];
      attributes = [];
      clone_data = null;
      $scope.last_select_attr = null;
      prefix = 'attribute-';
      selector_el = '.dropdown-menu.inner';
      $http.post($location.absUrl()).success(function(data) {
        clone_data = data;
        if (data.price) {
          $scope.product.price = data.price;
        } else {
          $scope.product.product_not_availability = data.product_not_availability;
        }
        return angular.forEach(data.attributes, function(attr) {
          var el, element;
          attributes.push(attr.id);
          $scope.product.values[attr.id] = attr.values;
          $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0];
          if (data.product_version_attributes[attr.id]) {
            $scope.product.attributes[attr.id] = data.product_version_attributes[attr.id];
          }
          element = angular.element(document).find("[data-id='" + prefix + attr.id + "']");
          element.parent().find(selector_el + ' li:not(:first)').remove();
          el = angular.element(document).find('#' + prefix + attr.id);
          el.attr('ng-model', 'product.attributes[' + attr.id + ']');
          el.attr('ng-options', 'value.title group by value.group for value in product.values[' + attr.id + '] track by value.id');
          el.attr('ng-change', 'last_select_attr=' + attr.id);
          $compile(el)($scope);
          el = element.find('.filter-option');
          el.attr('ng-bind', 'product.attributes[' + attr.id + '].title');
          $compile(el)($scope);
          el = element.parent().find(selector_el + ' li:first');
          el.attr('ng-repeat', 'val in product.values[' + attr.id + ']');
          el.attr('data-original-index', "{{$index}}");
          el.find('a .text').attr('ng-bind', "val.title");
          return $compile(el)($scope);
        });
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      set_price = function() {
        var exist_selected_attr, selected_attributes;
        selected_attributes = [];
        angular.forEach(attributes, function(key) {
          if ($scope.product.attributes[key].id !== 0) {
            return selected_attributes.push($scope.product.attributes[key].id);
          }
        });
        exist_selected_attr = clone_data.product_versions[selected_attributes.toString()];
        if (exist_selected_attr) {
          $scope.product.price = clone_data.product_versions[selected_attributes.toString()];
        }
        return exist_selected_attr;
      };
      return $scope.update_price = function() {
        if (!set_price()) {
          angular.forEach(clone_data.variant_attributes[$scope.product.attributes[$scope.last_select_attr].id], function(attr) {
            $scope.product.values[attr.id] = attr.values;
            if (attr.in_group[1] && attr.in_group[1].first_visible) {
              return $scope.product.attributes[attr.id] = attr.in_group[1];
            } else if ($scope.product.values[attr.id]) {
              return $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0];
            }
          });
          if (!set_price()) {
            $scope.product.price = clone_data.price;
            angular.forEach(clone_data.attributes, function(attr) {
              $scope.product.values[attr.id] = attr.values;
              $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0];
              if (clone_data.product_version_attributes[attr.id]) {
                return $scope.product.attributes[attr.id] = clone_data.product_version_attributes[attr.id];
              }
            });
          }
          return console.log('choose the option with the lowest price');
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
