'use strict'

### Controllers ###

app_name = 'soloha'
app = angular.module app_name, []

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.controller 'Product', ['$http', '$scope', '$window', '$document', '$location', ($http, $scope, $window, $document, $location) ->
  $scope.product = []
  $scope.product.price = '12'

  $http.post($location.absUrl()).success (data) ->
    console.log(data)
  .error ->
    console.error('An error occurred during submission')
]
