'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module app_name

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.controller 'Search', ['$http', '$scope', '$window', '$document', '$location', '$routeParams', ($http, $scope, $window, $document, $location, $routeParams) ->

  $http.post($location.absUrl()).success (data) ->
#    console.log($scope.search_string)
    $scope.products = data.products
    console.log($scope.products)
    $scope.page_number = data.page_number
  .error ->
    console.error('An error occurred during submission')

  $scope.submit = ->
    $http.post($location.absUrl(), {'search_string': $scope.search_string, 'more_goods': goods}).success (data) ->
      id = angular.element(document).find('id')
      href = angular.element(document).find('href')
      title = angular.element(document).find('title')
      image = angular.element(document).find('image')
      items = angular.element(document).find('row items')
      items.attr('ng-repeat', 'product in products')
      id.innerHTML='data.product.id'
      href.innerHTML='data.product.href'
      title.innerHTML='data.product.title'
      image.innerHTML='data.product.image'
      console.log($scope.products)
      console.log($scope.page_number)
    .error ->
      console.error('An error occurred during submission')
]
