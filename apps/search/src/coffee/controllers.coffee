'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module app_name

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.controller 'Search', ['$http', '$scope', '$window', '$document', '$location', ($http, $scope, $window, $document, $location) ->

  $http.get($location.absUrl(), {'search_string': $scope.search_string, 'test': 'test data'}).success (data) ->
      console.log(data)
  .error ->
      console.error('An error occurred during submission')

  $scope.submit = ->
    $http.post($location.absUrl(), {'search_string': $scope.search_string, 'more_goods': $scope.more_goods}).success (data) ->
      $scope.search_string = data.search_string
      $scope.more_goods = data.more_goods
      console.log(data)
      console.log($location.absUrl())
    .error ->
      console.error('An error occurred during submission')

]
