(function() {
  'use strict';

  /* Declare app level module which depends on filters, and services */


}).call(this);


/* Controllers */

(function() {
  var app, app_name;

  app_name = 'soloha';

  app = angular.module(app_name, ['ngResource', 'ngRoute', 'ng.django.forms', 'ui.bootstrap', 'ngAnimate', 'duScroll']);

  app.config([
    '$httpProvider', function($httpProvider) {
      $httpProvider.defaults.xsrfCookieName = 'csrftoken';
      $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
      return $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    }
  ]);

  app.controller('Header', [
    '$http', '$scope', '$location', '$window', '$document', '$log', '$cacheFactory', '$route', function($http, $scope, $location, $window, $document, $log, $cacheFactory, $route) {
      return $scope.update_products = function() {
        return $http.post('/search/', {
          'search_string': $scope.search
        }).success(function(data) {
          $scope.search_string = data.search_string;
          $scope.sorting_type = data.sorting_type;
          $scope.searched_products = data.searched_products;
          if ($scope.searched_products.length && $scope.search) {
            return $scope.display = 'block';
          } else {
            return $scope.display = 'none';
          }
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
          angular.forEach(data.attributes, function(attr) {});
          el = angular.element($('[ng-model="option_model[' + 69 + ']" '));
          el.remove();
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

  app = angular.module(app_name);

  app.config([
    '$httpProvider', function($httpProvider) {
      $httpProvider.defaults.xsrfCookieName = 'csrftoken';
      $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
      return $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    }
  ]);

  app.controller('Contacts', [
    '$http', '$scope', '$window', 'djangoForm', '$document', function($http, $scope, $window, djangoForm, $document) {
      $scope.alerts = [];
      $scope.closeAlert = function(index) {
        return $scope.alerts.splice(index, 1);
      };
      return $scope.submit = function() {
        $scope.disabled = true;
        if ($scope.feedback) {
          $http.post(".", $scope.feedback).success(function(data) {
            var duration, offset, someElement;
            if (!djangoForm.setErrors($scope.form_comment, data.errors)) {
              duration = 800;
              offset = 0;
              $scope.alerts.push({
                msg: data.msg,
                type: 'success'
              });
              someElement = angular.element(document.getElementById('alerts'));
              return $document.scrollToElement(someElement, offset, duration);
            }
          }).error(function() {
            return console.error('An error occurred during submission');
          });
        }
        $scope.disabled = false;
        return false;
      };
    }
  ]);

  app.directive('alertSuccess', ['$scope', function($scope) {}]);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = "soloha";

  app = angular.module(app_name);

  app.controller('Home', ['$http', '$scope', '$window', '$document', '$log', function($http, $scope, $window, $document, $log) {}]);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = "soloha";

  app = angular.module(app_name);

  app.config([
    '$httpProvider', function($httpProvider) {
      $httpProvider.defaults.xsrfCookieName = 'csrftoken';
      $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
      return $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    }
  ]);

  app.controller('Search', [
    '$http', '$scope', '$window', '$document', '$location', function($http, $scope, $window, $document, $location) {
      return $scope.submit = function() {
        return $http.post($location.absUrl(), {
          'search_string': $scope.search_string
        }).success(function(data) {
          $scope.search_string = data.search_string;
          console.log(data);
          return console.log($location.absUrl());
        }).error(function() {
          return console.error('An error occurred during submission');
        });
      };
    }
  ]);

}).call(this);
