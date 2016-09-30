'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module app_name

app.controller 'Contacts', ['$http', '$scope', '$window', 'djangoForm', '$document', ($http, $scope, $window, djangoForm, $document) ->
    $scope.alert = null
    $scope.disabled_button = false

    $scope.remove_alert = ->
        $scope.alert = null

    $scope.submit = ->
        if $scope.feedback
            $scope.disabled_button = true
            $scope.alert = null
            $scope.button.actual = $scope.button.sending

            $http.post(".", $scope.feedback).success (data) ->
                if not djangoForm.setErrors($scope.form_comment, data.errors)
                    $scope.alert = ({msg: data.msg, type: 'alert-success'})

                $scope.button.actual = $scope.button.send
                $scope.disabled_button = false
            .error ->
                console.error('An error occurred during submission')

]
app.directive 'alertSuccess', ['$scope', ($scope) ->
]
