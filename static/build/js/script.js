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
      news = djangoUrl.reverse('promotions:new');
      $http.post(news).success(function(products) {
        $scope.products = products;
        return $scope.news = products;
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      $http.post(recommends).success(function(products) {
        return $scope.recommends = products;
      }).error(function() {
        return console.error('An error occurred during submission');
      });
      $scope.get_news = function() {
        return $scope.products = $scope.news;
      };
      $scope.get_recommends = function() {
        return $scope.products = $scope.recommends;
      };
      $scope.get_special = function() {
        return $scope.products = [];
      };
      return $scope.get_hits = function() {
        return $scope.products = [];
      };
    }
  ]);

}).call(this);
