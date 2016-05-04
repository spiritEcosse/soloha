'use strict'

### Controllers ###

app_name = 'soloha'
app = angular.module app_name, ['ngResource']

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]


app.controller 'Product', ['$http', '$scope', '$window', '$document', '$location', '$compile', ($http, $scope, $window, $document, $location, $compile) ->
  $scope.product = []
  $scope.product.values = []
  $scope.product.attributes = []
  selected_attributes = []
  attributes = []
  product_versions = []

  $http.post($location.absUrl()).success (data) ->
    if data.price
      $scope.product.price = data.price
    else
      $scope.product.product_not_availability = data.product_not_availability
    product_versions = data.product_versions

    console.log($scope.product.price)

    angular.forEach data.attributes, (attr) ->
      attributes.push(attr.pk)
      $scope.product.values[attr.pk] = attr.values
      $scope.product.attributes[attr.pk] = $scope.product.values[attr.pk][0]
      el = angular.element(document).find('#attribute-' + attr.pk)
      el.attr('ng-model', 'product.attributes[' + attr.pk + ']')
      el.attr('ng-options', 'value.title for value in product.values[' + attr.pk + '] track by value.id')
      el.attr('ng-change', 'update_price()')
      $compile(el)($scope)
  .error ->
    console.error('An error occurred during submission')

  $scope.update_price = () ->
    selected_attributes = []
    angular.forEach attributes, (key) ->
      selected_attributes.push($scope.product.attributes[key].id)
    $scope.product.price = product_versions[selected_attributes.toString()]
]
