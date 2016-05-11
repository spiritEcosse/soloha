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

      if data.product_version_attributes[attr.pk]
        $scope.product.attributes[attr.pk] = data.product_version_attributes[attr.pk]

      console.log($scope.product.values[attr.pk][0])
      el = angular.element(document).find('#attribute-' + attr.pk)
      el.attr('ng-model', 'product.attributes[' + attr.pk + ']')
      el.attr('ng-options', 'value.title group by value.group for value in product.values[' + attr.pk + '] track by value.id')
      el.attr('ng-change', 'update_price()')
      $compile(el)($scope)
  .error ->
    console.error('An error occurred during submission')

  $scope.update_price = () ->
    selected_attributes = []
    angular.forEach attributes, (key) ->
      console.log($scope.product.attributes[key].id)

      if $scope.product.attributes[key].id != 0
        selected_attributes.push($scope.product.attributes[key].id)
    #Todo igor: if selected_attributes is empty - message select - attribute for display price
    $scope.product.price = product_versions[selected_attributes.toString()]
]
