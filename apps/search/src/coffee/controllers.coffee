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
    $scope.initial_page_number = data.page_number
    $scope.page_number = data.page_number
    $scope.num_pages = data.num_pages
    $scope.search_string = data.search_string
    $scope.pages = [data.pages[parseInt($scope.initial_page_number)-1]]
    $scope.pages[0].active = "True"
    $scope.pages[0].link = ""
    $scope.sorting_type = data.sorting_type
  .error ->
    console.error('An error occurred during submission')

  $scope.submit = ->
    $http.post($location.absUrl(), {'search_string': $scope.search_string, 'page': $scope.page_number, 'sorting_type': $scope.sorting_type}).success (data) ->
      clear = angular.element('.clear_pagination')
      clear.remove()
      $scope.pages = data.pages
      for page_active in [parseInt($scope.initial_page_number)-1..parseInt($scope.page_number)]
        $scope.pages[page_active].active = "True"
        $scope.pages[page_active].link = ""
      $scope.products = $scope.products.concat data.products_next_page
      $scope.page_number = parseInt($scope.page_number)+1
      if $scope.page_number == parseInt($scope.num_pages)
        $scope.hide=true
      console.log($scope.pages)
    .error ->
      console.error('An error occurred during submission')
]
