(function() {
  'use strict';

  /* Declare app level module which depends on filters, and services */


}).call(this);


/* Controllers */

(function() {
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

  app.controller('Header', [
    '$http', '$scope', '$location', '$window', '$document', '$log', '$cacheFactory', function($http, $scope, $location, $window, $document, $log, $cacheFactory) {
      return $scope.update_products = function() {
        return $http.post('/search/', {
          'search_string': $scope.search
        }).success(function(data) {
          console.log(data);
          $scope.search_string = data.search_string;
          if (data.searched_products) {
            $scope.searched_products = data.searched_products;
          }
          console.log($scope.searched_products);
          return console.log($scope.search_string);
        }).error(function() {
          return console.error('An error occurred during submission');
        });
      };
    }
  ]);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = 'soloha';

  app = angular.module(app_name);

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
      $http.post($location.absUrl()).success(function(data) {
        $scope.options = data.options;
        $scope.options_children = data.options_children;
        $scope.list_options = data.list_options;
        if (data.price) {
          return $scope.new_price = data.price;
        } else {
          return $scope.product.product_not_availability = data.product_not_availability;
        }
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      $scope.change_price = function(option_id) {
        console.log(option_id);
        if (Object.keys($scope.options_children).length !== 0) {
          $scope.option_id = Object.keys($scope.options_children[$scope.option_id]).filter(function(key) {
            return $scope.options_children[$scope.option_id][key] === $scope.option_model[$scope.option_id];
          })[0];
        } else if ($scope.option_id) {
          $scope.option_id = $scope.model[$scope.option_id];
        } else {
          $scope.option_id = $scope.model[0];
        }
        if ($scope.options[$scope.option_id]) {
          $scope.new_price += parseFloat($scope.options[$scope.option_id]);
        } else {
          $scope.parent = true;
        }
        return $http.post($location.absUrl(), {
          'option_id': $scope.option_id,
          'parent': $scope.parent,
          'list_options': $scope.list_options
        }).success(function(data) {
          $scope.options = data.options;
          $scope.options_children[$scope.option_id] = data.options_children;
          if (Object.keys($scope.options_children[$scope.option_id]).length !== 0) {
            delete $scope.list_options[$scope.option_id];
            return angular.element(document.getElementById('options-0')).append($compile('<span id="' + $scope.option_id + '"> <select class="form-control" ng-model="option_model[' + $scope.option_id + ']" ng-change="change_price(option_id)" ng-options="option for option in options_children[' + $scope.option_id + ']" ></select> </span>')($scope));
          } else {
            console.log("new");
            delete $scope.list_options[$scope.option_id];
            return angular.element(document.getElementById('options-0')).append($compile('<div id="model[' + $scope.option_id + ']"> <select class="form-control" ng-model="option_model[' + $scope.option_id + ']" ng-change="change_price(option_id)" ng-options="option for option in list_options" ></select> </div>')($scope));
          }
        }).error(function() {
          var el, model;
          console.error('An error occurred during submission');
          angular.element(document.getElementById('options-0')).remove(ng - (model = "option_model[' + $scope.option_id + ']"));
          console.log(el);
          angular.forEach(data.attributes, function(attr) {});
          el = angular.element($('[ng-model="option_model[' + 69 + ']" '));
          el.remove();
          console.log(el);
          el = angular.element($('[ng-model="option_model[' + $scope.option_id + ']"'));
          el = angular.element($('[ng-model="confirmed"'));
          console.log(el.find('div').remove());
          angular.element(document.getElementById('options-0')).append($compile('<div id="' + $scope.option_id + '"> <select class="form-control" ng-model="option_model[' + $scope.option_id + ']" ng-change="change_price()" ng-options="option for option in options_children[' + $scope.option_id + ']" ></select> </div>')($scope));
          console.log(this.find('div'));
          el = angular.element($('[ng-model="' + $scope.option_id + '" '));
          model = el;
          console.log(model);
          console.log($scope.model);
          el = angular.element(document).find('#tests');
          $scope.test = 12;
          console.log($scope.test);
          el.remove();
          console.log($scope.test);
          return angular.element(document.getElementById('options-0')).append($compile('<select class="form-control" ng-model="option_model[' + $scope.option_id + ']" ng-change="change_price()" ng-options="option for option in options_children[' + $scope.option_id + ']" ></select>')($scope));
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

  app = angular.module(app_name);

  app.controller('Home', ['$http', '$scope', '$window', '$document', '$log', function($http, $scope, $window, $document, $log) {}]);

}).call(this);
