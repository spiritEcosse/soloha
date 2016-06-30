'use strict'

### Controllers ###


app_name = "soloha"
#app = angular.module app_name, ['ngResource']
app = angular.module app_name
#app = angular.module app_name, ["#{app_name}.controllers"]


app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.controller 'Subscribe', ['$http', '$scope', '$window', 'djangoForm', '$document', '$location', ($http, $scope, $window, djangoForm, $document, $location) ->
  $scope.subscribe = () ->
    if $scope.subscribe_data
        $http.post('/', $scope.subscribe_data).success((out_data) ->
            if !djangoForm.setErrors($scope.subscribe_form, out_data.errors)
                $scope.send_form = true
        ).error ->
            console.error 'An error occured during submission'
]


#app.controller 'Home', ['$http', '$scope', '$window', '$document', '$log', ($http, $scope, $window, $document, $log) ->
#app.controller 'Home', ['$http', '$scope', '$window', '$document', '$log', 'djangoUrl', ($http, $scope, $window, $document, $log, djangoUrl) ->
#  hits = djangoUrl.reverse('promotions:hits')
#  recommends = djangoUrl.reverse('promotions:recommend')
#  news = djangoUrl.reverse('promotions:new')


#  $http.post(news).success (products) ->
#    $scope.products = products
#    $scope.news = products
#  .error ->
#    console.error('An error occurred during submission')
#

#  $http.post(recommends).success (products) ->
#    $scope.recommends = products
#  .error ->
#    console.error('An error occurred during submission')

  #  $http.post(hits).success (products) ->
  #    $scope.hits = products
  #  .error ->
  #    console.error('An error occurred during submission')

#  $scope.get_news = ->
#    $scope.products = $scope.news
#
#  $scope.get_recommends = ->
#    $scope.products = $scope.recommends
#
#  $scope.get_special = ->
#    $scope.products = []
#
#  $scope.get_hits = ->
#    $scope.products = []

#]
