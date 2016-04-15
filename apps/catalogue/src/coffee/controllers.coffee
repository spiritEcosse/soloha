'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module app_name, []

app.controller 'Product', ['$http', '$scope', '$location', '$window', '$document', '$log',
  ($http, $scope, $location, $window, $document, $log) ->
    $scope.product = []
    $scope.product.price = '12'

    console.log($location.absUrl())

    $http.post('http://127.0.0.1:8000/category-1/category-12/category-123/product-1', message='test')

    $http.post($location.absUrl()).success (data) ->
      console.log(data)
      $scope.products = data.products
      $scope.paginator = data.paginator
    .error ->
      console.error('An error occurred during submission')
]
