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

  myVar = document.getElementById("myVar").value

#  $http.get($location.absUrl(), {'search_string': $scope.search_string}).success (data) ->
#      console.log(data)
#      console.log(myVar)
#      console.log($location.absUrl())
#  .error ->
#      console.error('An error occurred during submission')

  $scope.submit = ->
    $http.post($location.absUrl(), {'search_string': $scope.search_string, 'page_obj_next': $scope.page_obj_next}).success (data) ->
      $scope.search_string = data.search_string
      $scope.more_goods = data.more_goods
      $scope.page_obj_next = myVar
      console.log(data)
    .error ->
      console.error('An error occurred during submission')

]
