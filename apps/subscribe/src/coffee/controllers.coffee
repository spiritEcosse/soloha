'use strict'

### Controllers ###


app_name = "soloha"
app = angular.module app_name


app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.controller 'Subscribe', ['$http', '$scope', '$window', 'djangoForm', '$document', '$location', ($http, $scope, $window, djangoForm, $document, $location) ->
  $scope.subscribe = () ->
    if $scope.subscribe_data
        $http.post('/subscribe/', $scope.subscribe_data).success((out_data) ->
            if !djangoForm.setErrors($scope.subscribe_form, out_data.errors)
                $scope.send_form = true
        ).error ->
            console.error 'An error occured during submission'
]
