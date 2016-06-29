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

# Here should be other controller (something like quick order)
app.controller 'Subscribe', ['$http', '$scope', '$window', 'djangoForm', '$document', ($http, $scope, $window, djangoForm, $document) ->
  $scope.closeAlert = (index) ->
    $scope.alerts.splice(index, 1)

#  $scope.disabled = true

  $scope.submit = ->
    $scope.disabled = true

    if $scope.subscribe
      $http.post(".", $scope.subscribe).success (data) ->
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
