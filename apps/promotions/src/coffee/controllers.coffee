'use strict'

### Controllers ###

app_name = "promotions"
app = angular.module "#{app_name}.controllers", []

app.controller 'Home', ['$http', '$scope', '$window', '$document', '$log', 'djangoUrl', ($http, $scope, $window, $document, $log, djangoUrl) ->
  hits = djangoUrl.reverse('promotions:hits')
  recommends = djangoUrl.reverse('promotions:recommend')
  news = djangoUrl.reverse('promotions:new')

  $http.post(news).success (products) ->
    $scope.products = products
    $scope.news = products
#    slider.refresh()
  .error ->
    console.error('An error occurred during submission')

  $http.post(recommends).success (products) ->
    $scope.recommends = products
  .error ->
    console.error('An error occurred during submission')

  #  $http.post(hits).success (products) ->
  #    $scope.hits = products
  #  .error ->
  #    console.error('An error occurred during submission')

  $scope.get_news = ->
    $scope.products = $scope.news

  $scope.get_recommends = ->
    $scope.products = $scope.recommends

  $scope.get_special = ->
    $scope.products = []

  $scope.get_hits = ->
    $scope.products = []

]