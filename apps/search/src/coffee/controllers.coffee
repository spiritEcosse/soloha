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

  goods = document.getElementById("goods").value

  $scope.submit = ->
    $http.post($location.absUrl(), {'search_string': $scope.search_string, 'more_goods': goods}).success (data) ->
      $scope.search_string = data.search_string
      $scope.more_goods = goods
#      $scope.page_obj_next = goods
      console.log($scope.more_goods)
#      console.log(goods)
    .error ->
      console.error('An error occurred during submission')

#    $http.get($location.absUrl(), {'search_string': $scope.search_string, 'more_goods': goods}).success (data) ->
#      console.log(data)
#      console.log(goods)
#      console.log($location.absUrl())
#    .error ->
#      console.error('An error occurred during submission')
]
