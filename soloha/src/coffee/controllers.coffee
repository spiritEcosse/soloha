'use strict'

app_name = 'soloha'
app = angular.module app_name

app.controller 'Header', ['$http', '$scope', '$location', '$window', '$document', '$log', '$cacheFactory', ($http, $scope, $location, $window, $document, $log, $cacheFactory) ->
    $scope.update_products = () ->
        $('#search-dropdown').addClass('open')
        $scope.searched_products = []

        $http.post('/search/', {'search_string': $scope.search}).success (data) ->
            $scope.sorting_type = data.sorting_type
            $scope.searched_products = data.searched_products
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


