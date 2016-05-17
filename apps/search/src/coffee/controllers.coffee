app_name = 'soloha'
app = angular.module app_name

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.controller 'Product', ['$http', '$scope', '$window', '$document', '$location', '$compile', ($http, $scope, $window, $document, $location, $compile) ->
    $scope.submit = ->
      $scope.disabled = true

    $http.post(".", $scope.more_goods).success (data) ->
      duration = 800
      offset = 0
      $scope.alerts.push({msg: data.msg, type: 'success'})
      someElement = angular.element(document.getElementById('alerts'))
      $document.scrollToElement(someElement, offset, duration)
    .error ->
      console.error('An error occurred during submission')

    $scope.disabled = false
    return false
]
