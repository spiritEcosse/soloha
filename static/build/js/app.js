(function() {
  'use strict';

  /* Declare app level module which depends on filters, and services */
  var app, app_name;

  app_name = 'soloha';

  app = angular.module(app_name, [app_name + ".controllers", 'ng.django.urls']);

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

  app = angular.module(app_name + ".controllers", []);

  app.controller('Header', [
    '$http', '$scope', '$window', '$document', '$log', 'djangoUrl', function($http, $scope, $window, $document, $log, djangoUrl) {
      var categories;
      categories = djangoUrl.reverse('promotions:categories');
      return $http.post(categories).success(function(categories) {
        return $scope.categories = categories;
      }).error(function() {
        return console.log('An error occurred during submission');
      });
    }
  ]);

}).call(this);
