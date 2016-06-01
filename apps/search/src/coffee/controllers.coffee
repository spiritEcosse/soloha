'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module app_name

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.controller 'Search', ['$http', '$scope', '$window', '$document', '$location', '$routeParams', '$compile', ($http, $scope, $window, $document, $location, $routeParams, $compile) ->
  $scope.page_numbers = []

  $http.post($location.absUrl()).success (data) ->
    items = angular.element(document).find('#product')
    items.attr('ng-repeat', 'product in products')
    $compile(items)($scope)
    clear = angular.element('.clear')
    clear.remove()
    $scope.products = data.products
    $scope.page_number = data.page_number
    $scope.page_range = data.page_range
#    $scope.page_range = Object.keys($scope.page_range)

#    $scope.page_numbers.push parseInt($scope.page_number)
#    $scope.page_range.pop parseInt($scope.page_number)
  .error ->
    console.error('An error occurred during submission')

  $scope.submit = ->
    $http.post($location.absUrl(), {'search_string': $scope.search_string, 'page': $scope.page_number}).success (data) ->
      clear = angular.element('.clear_pagination')
      clear.remove()
      $scope.products = $scope.products.concat data.products_next_page
      $scope.page_number = parseInt($scope.page_number)+1
      $scope.pages = data.pages
      console.log($scope.pages)
#      $scope.page_range.splice($scope.page_range.indexOf($scope.page_number), 1)
    .error ->
      console.error('An error occurred during submission')
]
