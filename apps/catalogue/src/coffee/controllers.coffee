'use strict'

### Controllers ###

app_name = 'soloha'
app = angular.module app_name, ['ngResource']

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.factory 'Product', ['$resource', ($resource) ->
    $resource '/catalogue/crud/product/', { 'pk': '@pk' }, {}
]

app.controller 'Product', ['$http', '$scope', '$window', '$document', '$location', 'Product', ($http, $scope, $window, $document, $location, Product) ->
  $scope.product = Product.get({pk: 3})
  console.log($scope.product)

  $http.post($location.absUrl()).success (data) ->
    console.log(data)
  .error ->
    console.error('An error occurred during submission')
]
