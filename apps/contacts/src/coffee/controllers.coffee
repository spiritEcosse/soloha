'use strict'

### Controllers ###

app_name = "soloha"
#app = angular.module "#{app_name}.controllers", ['djng.forms']
app = angular.module app_name

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.controller 'Contacts', ['$http', '$scope', '$window', 'djangoForm', '$document', ($http, $scope, $window, djangoForm, $document) ->
  $scope.alerts = []

  $scope.closeAlert = (index) ->
    $scope.alerts.splice(index, 1)

  $scope.submit = ->
    $scope.disabled = true

    if $scope.feedback
      $http.post(".", $scope.feedback).success (data) ->
        if not djangoForm.setErrors($scope.form_comment, data.errors)
          console.log(data.msg)
          duration = 800
          offset = 0
          $scope.alerts.push({msg: data.msg, type: 'success'})
          someElement = angular.element(document.getElementById('alerts'))
          console.log(someElement)
          $document.scrollToElement(someElement, offset, duration)
#          $document.scrollToElement(someElement, 30, 500).then ->
#            console.log('You just scrolled to chart-help!')
      .error ->
        console.error('An error occurred during submission')

    $scope.disabled = false
    return false
]
app.directive 'alertSuccess', ['$scope', ($scope) ->

]