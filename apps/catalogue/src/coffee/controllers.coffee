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

  $scope.new_price = 1

  $scope.change_price = ->
    $scope.option_id = $scope.confirmed

    console.log($scope.option_id)
    if $scope.options[$scope.option_id]
      $scope.new_price += parseFloat($scope.options[$scope.option_id])
    else
      $scope.parent = true
    $http.post($location.absUrl(), {'option_id': $scope.option_id, 'parent': $scope.parent}).success (data) ->
      $scope.options = data.options
      $scope.options_children = data.options_children
    .error ->
      console.error('An error occurred during submission')


  $http.post($location.absUrl()).success (data) ->
    $scope.options = data.options
  .error ->
    console.error('An error occurred during submission')
]


