'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module app_name, []

app.factory('superCache', ['$cacheFactory', ($cacheFactory) ->
  return $cacheFactory 'super-cache'
])

app.controller 'Header', ['$http', '$scope', '$location', '$window', '$document', '$log', '$cacheFactory', 'djangoUrl', ($http, $scope, $location, $window, $document, $log, $cacheFactory, djangoUrl) ->
  categories = djangoUrl.reverse('promotions:categories')
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
]


