'use strict'

### Controllers ###

app_name = 'soloha'
app = angular.module app_name, ['ngResource']

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.controller 'Product', ['$http', '$scope', '$window', '$document', '$location', 'Product', ($http, $scope, $window, $document, $location, Product) ->
  $scope.product = []

  $http.get($location.absUrl()).then (response) ->
    $scope.options = response.data.options
    $scope.price = response.data.price
    return $scope.options

  $scope.product.price = 222
  console.log('test')

  $http.post($location.absUrl()).success (data) ->
    console.log(data)
  .error ->
    console.error('An error occurred during submission')
]


