'use strict'

### Controllers ###

app_name = 'soloha'
app = angular.module app_name, ['ngResource']

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.controller 'Product', ['$http', '$scope', '$window', '$document', '$location', ($http, $scope, $window, $document, $location) ->
  $scope.product = []

  $http.post($location.absUrl()).success (data) ->
    console.log(data)
    $scope.new_price = 1
    $scope.options = data.options
    $scope.change_price = ->
      $scope.option_id = $scope.confirmed
      if $scope.options[$scope.option_id]
        $scope.new_price += parseFloat($scope.options[$scope.option_id])
  .error ->
    console.error('An error occurred during submission')
]


