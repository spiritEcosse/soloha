(function() {
  'use strict';

  /* Declare app level module which depends on filters, and services */
  var app, app_name;

  app_name = 'soloha';

  app = angular.module(app_name, ['ng.django.urls', 'ui.bootstrap']);

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

  app_name = "soloha";

  app = angular.module(app_name, []);

  app.factory('superCache', [
    '$cacheFactory', function($cacheFactory) {
      return $cacheFactory('super-cache');
    }
  ]);

  app.controller('Header', [
    '$http', '$scope', '$location', '$window', '$document', '$log', '$cacheFactory', 'djangoUrl', function($http, $scope, $location, $window, $document, $log, $cacheFactory, djangoUrl) {
      var categories;
      return categories = djangoUrl.reverse('promotions:categories');
    }
  ]);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = "soloha";

  app = angular.module(app_name, []);

  app.controller('Catalogue', [
    '$http', '$scope', '$location', '$window', '$document', '$log', 'djangoUrl', function($http, $scope, $location, $window, $document, $log, djangoUrl) {
      var products_url;
      products_url = djangoUrl.reverse('catalogue:products');
      return $scope.product = 'as';
    }
  ]);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = "soloha";

  app = angular.module(app_name + ".controllers", []);

  app.controller('Home', [
    '$http', '$scope', '$window', '$document', '$log', 'djangoUrl', function($http, $scope, $window, $document, $log, djangoUrl) {
      var hits, news, recommends;
      hits = djangoUrl.reverse('promotions:hits');
      recommends = djangoUrl.reverse('promotions:recommend');
      return news = djangoUrl.reverse('promotions:new');
    }
  ]);

}).call(this);
