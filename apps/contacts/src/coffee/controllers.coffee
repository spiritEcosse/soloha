'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module app_name

app.controller 'Contacts', ['$http', '$scope', '$window', 'djangoForm', '$document', ($http, $scope, $window, djangoForm, $document) ->
    $scope.alert = null
    button = 'Sent'
    $scope.button = button
    $scope.disabled_button = false

    $scope.remove_alert = ->
        $scope.alert = null

    $scope.submit = ->
        $scope.disabled_button = true
        console.log($scope.disabled_button)

        if $scope.feedback
#            $scope.button = 'Sending'

            $http.post(".", $scope.feedback).success (data) ->
                if not djangoForm.setErrors($scope.form_comment, data.errors)
                    $scope.alert = ({msg: data.msg, type: 'alert-success'})
            .error ->
                console.error('An error occurred during submission')

#            $scope.button = button
            $scope.disabled_button = false
        return false
]
app.directive 'alertSuccess', ['$scope', ($scope) ->
]