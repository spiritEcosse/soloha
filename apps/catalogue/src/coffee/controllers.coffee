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

  $scope.new_price = 1

  $http.post($location.absUrl(), {'option_id': $scope.option_id, 'parent': $scope.parent}).success (data) ->
    $scope.options = data.options
    $scope.options_children = data.options_children
  .error ->
    console.error('An error occurred during submission')

  $scope.change_price = ->
#    angular.element(document.getElementById('options-0')).append $compile('<select class=\'btn btn-default\'><option>www</option></select>')($scope)

    $scope.option_id = $scope.confirmed
    if $scope.options[$scope.option_id]
      $scope.new_price += parseFloat($scope.options[$scope.option_id])
    else
      $scope.parent = true

    $http.post($location.absUrl(), {'option_id': $scope.option_id, 'parent': $scope.parent}).success (data) ->
      $scope.options = data.options #
      if Object.keys(data.options_children).length != 0
        console.log(data.options_children)
        $scope.options_children = data.options_children
        angular.element(document.getElementById('options-0')).append $compile('<select class="form-control" ng-model="data[options_children.65]"
                                                ng-change="change_price()" ng-options="option for option in options_children" ></select>')($scope)

    .error ->
      console.error('An error occurred during submission')

#  angular.forEach data.options, (option) ->
#    el = angular.element(document).create('#option-' + option.id)
#    el.option('ng-model', 'product.options[' + option.id + ']')
#    el.option('ng-options', 'option for option in product.options[' + option.id + ']')
#    el.option('ng-change', 'change_price()')
#    $compile(el)($scope)

  $http.post($location.absUrl()).success (data) ->
    if data.price
      $scope.product.price = data.price
    else
      $scope.product.product_not_availability = data.product_not_availability
    product_versions = data.product_versions

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
