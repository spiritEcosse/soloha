#'use strict'

### Controllers ###

app_name = 'soloha'
#app = angular.module app_name
app = angular.module app_name, ['ngResource', 'ngRoute']

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.controller 'Header', ['$http', '$scope', '$location', '$window', '$document', '$log', '$cacheFactory', '$route', ($http, $scope, $location, $window, $document, $log, $cacheFactory, $route) ->
  $scope.update_products = () ->
    $http.post('/search/', {'search_string': $scope.search}).success (data) ->
      $scope.search_string = data.search_string
      $scope.sorting_type = data.sorting_type
      console.log(data.searched_products)
      $scope.display = 'none'
      if data.searched_products.length
        $scope.searched_products = data.searched_products
        $scope.display = 'block'
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


