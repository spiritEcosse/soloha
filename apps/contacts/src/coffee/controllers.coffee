'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module app_name

app.controller 'Contacts', ['$http', '$scope', '$window', 'djangoForm', '$document', ($http, $scope, $window, djangoForm, $document) ->
  $scope.alerts = []

  $scope.closeAlert = (index) ->
    $scope.alerts.splice(index, 1)

  $scope.submit = ->
    $scope.disabled = true

    if $scope.feedback
      $http.post(".", $scope.feedback).success (data) ->
        if not djangoForm.setErrors($scope.form_comment, data.errors)
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
app.directive 'alertSuccess', ['$scope', ($scope) ->
]