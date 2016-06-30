#'use strict'

### Controllers ###

app_name = 'soloha'
#app = angular.module app_name
app = angular.module app_name, ['ngResource', 'ngRoute', 'ng.django.forms', 'ui.bootstrap', 'ngAnimate', 'duScroll']

app.config ['$httpProvider', '$routeProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.controller 'Header', ['$http', '$scope', '$location', '$window', '$document', '$log', '$cacheFactory', ($http, $scope, $location, $window, $document, $log, $cacheFactory) ->
  $scope.update_products = () ->
    $http.post('/search/', {'search_string': $scope.search}).success (data) ->
      $scope.search_string = data.search_string
      $scope.sorting_type = data.sorting_type
      $scope.searched_products = data.searched_products
      if $scope.searched_products.length and $scope.search
        $scope.display = 'block'
      else
        $scope.display = 'none'
    .error ->
      console.error('An error occurred during submission')
]


#  categories = djangoUrl.reverse('promotions:categories')
#  cache = $cacheFactory('superCache')
#
#  if !cache.get("categories")
#    $http.post(categories, { cache: true}).success (categories) ->
#      $scope.categories = categories
#      console.log('not in cache')
#      cache.put("categories", categories)
#    .error ->
#      console.log('An error occurred during submission')
#  else
#    $scope.categories = cache.get("categories")
#]


