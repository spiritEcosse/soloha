'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module app_name, []

app.controller 'Product', ['$http', '$scope', '$location', '$window', '$document', '$log',
  ($http, $scope, $location, $window, $document, $log) ->
    $scope.product = []
    $scope.product.price = '12'

    console.log($location.absUrl())

    $http.post($location.absUrl()).success (data) ->
      console.log(data)
      $scope.products = data.products
      $scope.paginator = data.paginator
    .error ->
      console.error('An error occurred during submission')
]
