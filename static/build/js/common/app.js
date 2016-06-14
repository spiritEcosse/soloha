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
    '$httpProvider', '$routeProvider', function($httpProvider) {
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
      $scope.isOpen = [];
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
        var el;
        clone_data = data;
        if (data.price) {
          $scope.product.price = data.price;
          el = angular.element('#product_price');
          el.attr('ng-bind', 'product.price');
        } else {
          $scope.product.product_not_availability = data.product_not_availability;
          el = angular.element('#product_not_availability');
          el.attr('ng-bind', 'product.product_not_availability');
        }
        $compile(el)($scope);
        return angular.forEach(data.attributes, function(attr) {
          var dropdown, element, li;
          attributes.push(attr.pk);
          $scope.product.values[attr.pk] = attr.values;
          $scope.product.attributes[attr.pk] = $scope.product.values[attr.pk][0];
          if (data.product_version_attributes[attr.pk]) {
            $scope.product.attributes[attr.pk] = data.product_version_attributes[attr.pk];
          }
          element = angular.element(document).find("[data-id='" + prefix + attr.pk + "']");
          element.parent().find(selector_el + ' li:not(:first)').remove();
          dropdown = angular.element(document).find('#' + prefix + attr.pk);
          dropdown.attr('ng-click', "click(" + attr.pk + ")");
          dropdown.find('button .title').attr('ng-bind', 'product.attributes[' + attr.pk + '].title');
          dropdown.find('button .attr-pk').attr('ng-bind', 'product.attributes[' + attr.pk + '].pk');
          dropdown.find('.dropdown-menu input').attr('ng-model', "query_attr[" + attr.pk + "]");
          dropdown.find('.dropdown-menu li.list:not(:first)').remove();
          li = dropdown.find('.dropdown-menu li.list');
          $scope.isOpen[attr.pk] = false;
          li.find('a').attr('ng-click', 'update_price($index, "' + attr.pk + '")').html("{{value.title}}");
          li.attr('ng-repeat', 'value in product.values[' + attr.pk + '] | filter:query_attr[' + attr.pk + ']');
          li.attr('ng-class', '{"selected active": value.pk == product.attributes[' + attr.pk + '].pk}');
          $compile(dropdown)($scope);
          return $compile(li)($scope);
        });
      }).error(function() {
        console.error('An error occurred during submission');
        return $scope.click = function(attr_id) {
          return $scope.isOpen[attr_id] = true;
        };
      });
      set_price = function() {
        var exist_selected_attr, selected_attributes;
        selected_attributes = [];
        angular.forEach(attributes, function(key) {
          if ($scope.product.attributes[key].pk !== 0) {
            return selected_attributes.push($scope.product.attributes[key].pk);
          }
        });
        exist_selected_attr = clone_data.product_versions[selected_attributes.toString()];
        if (exist_selected_attr) {
          $scope.product.price = exist_selected_attr;
        }
        return exist_selected_attr;
      };
      return $scope.update_price = function(index, attr_pk) {
        var selected_attributes;
        if ($scope.product.values[attr_pk][index]) {
          $scope.product.attributes[attr_pk] = $scope.product.values[attr_pk][index];
        }
        angular.forEach(clone_data.variant_attributes[$scope.product.attributes[attr_pk].pk], function(attr) {
          return $scope.product.values[attr.pk] = attr.values;
        });
        if (!set_price()) {
          angular.forEach(clone_data.variant_attributes[$scope.product.attributes[attr_pk].pk], function(attr) {
            $scope.product.values[attr.pk] = attr.values;
            if (attr.in_group[1] && attr.in_group[1].visible) {
              return $scope.product.attributes[attr.pk] = attr.in_group[1];
            } else if ($scope.product.values[attr.pk]) {
              return $scope.product.attributes[attr.pk] = $scope.product.values[attr.pk][0];
            }
          });
          if (!set_price()) {
            $scope.product.price = clone_data.price;
            selected_attributes = [];
            angular.forEach(clone_data.attributes, function(attr) {
              $scope.product.values[attr.pk] = attr.values;
              $scope.product.attributes[attr.pk] = $scope.product.values[attr.pk][0];
              if (clone_data.product_version_attributes[attr.pk]) {
                $scope.product.attributes[attr.pk] = clone_data.product_version_attributes[attr.pk];
              }
              if ($scope.product.attributes[attr.pk].pk !== 0) {
                return selected_attributes.push($scope.product.attributes[attr.pk].pk);
              }
            });
            return $scope.product.price = clone_data.product_versions[selected_attributes.toString()];
          }
        }
      };
    }
  ]);

  app.directive('focusMe', function($timeout, $parse) {
    return {
      link: function(scope, element, attrs) {
        var model;
        model = $parse(attrs.focusMe);
        scope.$watch(model, function(value) {
          if (value === true) {
            $timeout(function() {
              element[0].focus();
            });
          }
        });
        element.bind('blur', function() {
          scope.$apply(model.assign(scope, false));
        });
      }
    };
  });

  app.controller('More_goods', [
    '$http', '$scope', '$window', '$document', '$location', '$compile', '$routeParams', function($http, $scope, $window, $document, $location, $compile, $routeParams) {
      var getParameterByName;
      getParameterByName = function(name, url) {
        var regex, results;
        if (!url) {
          url = window.location.href;
        }
        name = name.replace(/[\[\]]/g, '\\$&');
        regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)');
        results = regex.exec(url);
        if (!results) {
          return null;
        }
        if (!results[2]) {
          return '';
        }
        return decodeURIComponent(results[2].replace(/\+/g, ' '));
      };
      $scope.sorting_type = '-views_count';
      if (getParameterByName('sorting_type')) {
        $scope.sorting_type = getParameterByName('sorting_type');
      }
      $scope.page_number = '1';
      if (getParameterByName('page')) {
        $scope.page_number = getParameterByName('page');
      }
      console.log($scope.page_number);
      $http.post($location.absUrl(), {
        'page': $scope.page_number,
        'sorting_type': $scope.sorting_type
      }).success(function(data) {
        var clear, items;
        items = angular.element(document).find('#product');
        items.attr('ng-repeat', 'product in products');
        $compile(items)($scope);
        clear = angular.element('.clear');
        clear.remove();
        $scope.products = data.products;
        $scope.initial_page_number = data.page_number;
        $scope.num_pages = data.num_pages;
        $scope.pages = [data.pages[parseInt($scope.initial_page_number) - 1]];
        $scope.pages[0].active = "True";
        $scope.pages[0].link = "";
        $scope.sorting_type = data.sorting_type;
        return console.log(data);
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      $scope.submit = function() {
        return $http.post($location.absUrl(), {
          'page': $scope.page_number,
          'sorting_type': $scope.sorting_type
        }).success(function(data) {
          var clear, page_active, _i, _ref, _ref1;
          clear = angular.element('.clear_pagination');
          clear.remove();
          $scope.pages = data.pages;
          for (page_active = _i = _ref = parseInt($scope.initial_page_number) - 1, _ref1 = parseInt($scope.page_number); _ref <= _ref1 ? _i <= _ref1 : _i >= _ref1; page_active = _ref <= _ref1 ? ++_i : --_i) {
            $scope.pages[page_active].active = "True";
            $scope.pages[page_active].link = "";
          }
          $scope.products = $scope.products.concat(data.products_next_page);
          $scope.page_number = parseInt($scope.page_number) + 1;
          if ($scope.page_number === parseInt($scope.num_pages)) {
            return $scope.hide = true;
          }
        }).error(function() {
          return console.error('An error occurred during submission');
        });
      };
      return $scope.click_test_option = function() {
        return console.log('hello');
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
    '$http', '$scope', '$window', '$document', '$location', '$routeParams', '$compile', function($http, $scope, $window, $document, $location, $routeParams, $compile) {
      $http.post($location.absUrl()).success(function(data) {
        var clear, items;
        items = angular.element(document).find('#product');
        items.attr('ng-repeat', 'product in products');
        $compile(items)($scope);
        clear = angular.element('.clear');
        clear.remove();
        $scope.products = data.products;
        $scope.initial_page_number = data.page_number;
        $scope.page_number = data.page_number;
        $scope.num_pages = data.num_pages;
        $scope.search_string = data.search_string;
        $scope.pages = [data.pages[parseInt($scope.initial_page_number) - 1]];
        $scope.pages[0].active = "True";
        $scope.pages[0].link = "";
        $scope.sorting_type = data.sorting_type;
        return console.log($scope.pages);
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      return $scope.submit = function() {
        return $http.post($location.absUrl(), {
          'search_string': $scope.search_string,
          'page': $scope.page_number,
          'sorting_type': $scope.sorting_type
        }).success(function(data) {
          var clear, page_active, _i, _ref, _ref1;
          clear = angular.element('.clear_pagination');
          clear.remove();
          $scope.pages = data.pages;
          for (page_active = _i = _ref = parseInt($scope.initial_page_number) - 1, _ref1 = parseInt($scope.page_number); _ref <= _ref1 ? _i <= _ref1 : _i >= _ref1; page_active = _ref <= _ref1 ? ++_i : --_i) {
            $scope.pages[page_active].active = "True";
            $scope.pages[page_active].link = "";
          }
          $scope.products = $scope.products.concat(data.products_next_page);
          $scope.page_number = parseInt($scope.page_number) + 1;
          if ($scope.page_number === parseInt($scope.num_pages)) {
            return $scope.hide = true;
          }
        }).error(function() {
          return console.error('An error occurred during submission');
        });
      };
    }
  ]);

}).call(this);
