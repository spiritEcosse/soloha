(function() {
  'use strict';

  /* Declare app level module which depends on filters, and services */
  var app, app_name;

  app_name = 'soloha';

  app = angular.module(app_name, ['ngResource', 'ngRoute', 'ng.django.forms', 'ui.bootstrap', 'ngAnimate', 'duScroll', 'ng.django.urls']);

  app.config([
    '$httpProvider', function($httpProvider) {
      $httpProvider.defaults.xsrfCookieName = 'csrftoken';
      $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
      $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
      return $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
    }
  ]);

}).call(this);

(function() {
  'use strict';
  var app, app_name;

  app_name = 'soloha';

  app = angular.module(app_name);

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
  var app, app_name,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  app_name = 'soloha';

  app = angular.module(app_name);

  app.filter('search_by_title', function() {
    return function(list, needle) {
      var val;
      if (list && needle) {
        if (__indexOf.call([
          (function() {
            var _i, _len, _results;
            _results = [];
            for (_i = 0, _len = list.length; _i < _len; _i++) {
              val = list[_i];
              _results.push(val.title);
            }
            return _results;
          })()
        ][0], needle) >= 0) {
          return true;
        } else {
          return false;
        }
      }
      return null;
    };
  });

  app.filter('filter_attribute', function() {
    return function(list, needle) {
      var new_list, val;
      if (list && (needle != null) && needle !== '') {
        needle = needle.toString();
        new_list = [
          (function() {
            var _i, _len, _results;
            _results = [];
            for (_i = 0, _len = list.length; _i < _len; _i++) {
              val = list[_i];
              if (val.title.toString().indexOf(needle) > -1) {
                _results.push(val);
              }
            }
            return _results;
          })()
        ];
        if (new_list.length) {
          return new_list;
        } else {
          return false;
        }
      }
      return list;
    };
  });

  app.controller('Product', [
    '$http', '$scope', '$window', '$document', '$location', '$compile', '$filter', 'djangoForm', '$rootScope', 'djangoUrl', function($http, $scope, $window, $document, $location, $compile, $filter, djangoForm, $rootScope, djangoUrl) {
      var attributes, clone_attributes, clone_data, get_prod, set_price;
      $scope.product = [];
      $scope.product.values = [];
      $scope.product.attributes = [];
      $scope.attributes = [];
      attributes = [];
      clone_data = null;
      $scope.last_select_attr = null;
      $scope.isOpen = [];
      $scope.product.custom_values = [];
      $scope.product.custom_value = [];
      $scope.product.dict_attributes = [];
      $scope.query_attr = [];
      $scope.send_form = false;
      $scope.alert_mode = 'success';
      $scope.prod_images = [];
      $scope.product_primary_images = [];
      $scope.product_images = null;
      $rootScope.Object = Object;
      $rootScope.keys = Object.keys;
      $scope.sent_signal = [];
      clone_attributes = [];
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
          return $scope.new_price += parseFloat($scope.options[$scope.option_id]);
        } else {
          return $scope.parent = true;
        }
      };
      $http.post($location.absUrl()).success(function(data) {
        clone_data = data;
        $scope.options = data.options;
        $scope.options_children = data.options_children;
        $scope.list_options = data.list_options;
        $scope.attributes = data.attributes;
        angular.copy(data.attributes, clone_attributes);
        $scope.product = data.product;
        $scope.product.custom_values = $scope.isOpen = $scope.product.dict_attributes = $scope.product.custom_value = [];
        angular.forEach($scope.attributes, function(attr) {
          attributes.push(attr.pk);
          if (attr.selected_val.images.length) {
            $scope.product_images = {
              pk: attr.selected_val.images[0].pk
            };
          }
          $scope.product.dict_attributes[attr.pk] = attr;
          $scope.product.custom_value[attr.pk] = null;
          $scope.isOpen[attr.pk] = false;
          return $scope.product.custom_values[attr.pk] = [];
        });
        return $scope.price_start = set_price();
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      $scope.update_price_with_custom_val = function(attr_pk, value) {
        var selected_attributes;
        if (value != null) {
          $scope.product.attributes[attr_pk] = value;
        } else {
          $scope.product.attributes[attr_pk] = $scope.product.custom_value[attr_pk];
        }
        selected_attributes = [];
        angular.forEach(clone_data.attributes, function(attr) {
          var non_standard;
          non_standard = $scope.product.dict_attributes[attr.pk].non_standard;
          if ($scope.product.attributes[attr.pk].pk !== 0 && non_standard === true) {
            return selected_attributes.push($scope.product.attributes[attr.pk]);
          }
        });
        if (selected_attributes.length) {
          return $http.post('/catalogue/calculate/price/' + clone_data.product.pk, {
            'selected_attributes': selected_attributes,
            'current_attr': $scope.product.attributes[attr_pk]
          }).success(function(data) {
            var key, _ref, _results;
            if (data.error == null) {
              $scope.price = data.price;
              if ($scope.product.custom_value[attr_pk] && !$filter('search_by_title')($scope.product.custom_values[attr_pk], $scope.product.custom_value[attr_pk].title)) {
                return $scope.product.custom_values[attr_pk].push($scope.product.custom_value[attr_pk]);
              }
            } else {
              _ref = data.error;
              _results = [];
              for (key in _ref) {
                value = _ref[key];
                _results.push($scope.product.attributes[key].error = value);
              }
              return _results;
            }
          }).error(function() {
            return console.error('An error occurred during submission');
          });
        }
      };
      $scope.search = function(attr_pk) {
        if (($scope.query_attr[attr_pk] != null) && $scope.query_attr[attr_pk] !== '' && !$filter('search_by_title')($scope.product.custom_values[attr_pk], $scope.query_attr[attr_pk])) {
          return $scope.product.custom_value[attr_pk] = {
            'pk': -1,
            'title': $scope.query_attr[attr_pk],
            'parent': attr_pk
          };
        } else {
          return $scope.product.custom_value[attr_pk] = null;
        }
      };
      $scope.click_dropdown = function(attr_id) {
        return $scope.isOpen[attr_id] = $scope.isOpen[attr_id] === false ? true : false;
      };
      get_prod = function(selected_val) {
        if ((selected_val.products != null) && !selected_val.products.length || (selected_val.products == null)) {
          return $http.post('/catalogue/attr/' + selected_val.pk + '/product/' + clone_data.product.pk + '/').success(function(data) {
            selected_val.products = data.products;
            if (data.product_primary_images.length && (selected_val.images == null)) {
              $scope.product_images = {
                pk: data.product_primary_images[0].pk
              };
            }
            return selected_val.images = data.product_primary_images;
          }).error(function() {
            return console.error('An error occurred during submission');
          });
        }
      };
      $scope.attr_prod = function(value) {
        return get_prod(value);
      };
      $scope.attr_prod_images = function(value, product) {
        if ((product.images != null) && !product.images.length) {
          product.sent_signal = true;
          return $http.post('/catalogue/attr/product/' + product.pk + '/images/').success(function(data) {
            var images;
            product.sent_signal = false;
            images = data.images;
            if (!data.images.length) {
              images = null;
            }
            return product.images = images;
          }).error(function() {
            return console.error('An error occurred during submission');
          });
        }
      };
      set_price = function() {
        var exist_selected_attr, selected_attributes;
        selected_attributes = [];
        attributes = $filter('orderBy')($scope.attributes, 'pk');
        if (attributes.length) {
          angular.forEach(attributes, function(attribute) {
            if (attribute.selected_val.pk !== 0) {
              return selected_attributes.push(attribute.selected_val.pk);
            }
          });
          exist_selected_attr = clone_data.stockrecords[selected_attributes.toString()];
          if (exist_selected_attr) {
            $scope.price = exist_selected_attr.price;
            $scope.stockrecord = exist_selected_attr.stockrecord_id;
            return exist_selected_attr.price;
          }
        }
        return false;
      };
      $scope.update_price = function(value, current_attribute) {
        current_attribute.selected_val = value;
        get_prod(value);
        angular.forEach(clone_data.variant_attributes[value.pk], function(attr) {
          var attribute;
          attribute = $filter('filter')($scope.attributes, {
            pk: attr.pk
          })[0];
          return attribute.values = attr.values;
        });
        if (!set_price()) {
          angular.forEach(clone_data.variant_attributes[value.pk], function(attr) {
            var attribute;
            attribute = $filter('filter')($scope.attributes, {
              pk: attr.pk
            })[0];
            attribute.values = attr.values;
            if (attr.values[1] && attr.values[1].visible) {
              attribute.selected_val = attr.values[1];
            } else if (attribute.values) {
              attribute.selected_val = attribute.values[0];
            }
            return get_prod(attribute.selected_val);
          });
          if (!set_price()) {
            $scope.price = $scope.price_start;
            return angular.forEach($scope.attributes, function(attr) {
              var attribute;
              attribute = $filter('filter')(clone_attributes, {
                pk: attr.pk
              })[0];
              attr.values = attribute.values;
              attr.selected_val = attribute.selected_val;
              return get_prod(attribute.selected_val);
            });
          }
        }
      };
      $scope.quick_order = function() {
        if ($scope.quick_order_data) {
          return $http.post('/catalogue/quick/order/' + clone_data.product.pk, $scope.quick_order_data).success(function(out_data) {
            if (!djangoForm.setErrors($scope.quick_order_form, out_data.errors)) {
              return $scope.send_form = true;
            }
          }).error(function() {
            return console.error('An error occured during submission');
          });
        }
      };
      return $scope.change_wishlist = function() {
        if ($scope.active !== 'none') {
          return $http.post($scope.wish_list_url + 'products/' + $scope.product_id + '/delete/').success(function(data) {
            return $scope.active = 'none';
          }).error(function() {
            return console.error('An error occurred during submission');
          });
        } else {
          return $http.post('/accounts/wishlists/add/' + $scope.product_id + '/').success(function(data) {
            return $scope.active = "active";
          }).error(function() {
            return console.error('An error occurred during submission');
          });
        }
      };
    }
  ]);

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
        return $scope.sorting_type = data.sorting_type;
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      return $scope.submit = function() {
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
    }
  ]);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = "soloha";

  app = angular.module(app_name);

  app.controller('Contacts', [
    '$http', '$scope', '$window', 'djangoForm', '$document', function($http, $scope, $window, djangoForm, $document) {
      $scope.alert = null;
      $scope.disabled_button = false;
      $scope.remove_alert = function() {
        return $scope.alert = null;
      };
      return $scope.submit = function() {
        if ($scope.feedback) {
          $scope.disabled_button = true;
          $scope.alert = null;
          $scope.button.actual = $scope.button.sending;
          return $http.post(".", $scope.feedback).success(function(data) {
            if (!djangoForm.setErrors($scope.form_comment, data.errors)) {
              $scope.alert = {
                msg: data.msg,
                type: 'alert-success'
              };
            }
            $scope.button.actual = $scope.button.send;
            return $scope.disabled_button = false;
          }).error(function() {
            return console.error('An error occurred during submission');
          });
        }
      };
    }
  ]);

  app.directive('alertSuccess', ['$scope', function($scope) {}]);

}).call(this);

(function() {
  'use strict';
  var app, app_name;

  app_name = "soloha";

  app = angular.module(app_name);

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
        return $scope.sorting_type = data.sorting_type;
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

(function() {


}).call(this);
