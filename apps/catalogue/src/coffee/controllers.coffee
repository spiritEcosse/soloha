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
  attributes = []
  clone_data = null
  $scope.last_select_attr = null
  prefix = 'attribute-'
  selector_el = '.dropdown-menu.inner'

  $http.post($location.absUrl()).success (data) ->
    clone_data = data
    if data.price
      $scope.product.price = data.price
    else
      $scope.product.product_not_availability = data.product_not_availability

    angular.forEach data.attributes, (attr) ->
      attributes.push(attr.id)
      $scope.product.values[attr.id] = attr.values
      $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0]

      if data.product_version_attributes[attr.id]
        $scope.product.attributes[attr.id] = data.product_version_attributes[attr.id]

      element = angular.element(document).find("[data-id='" + prefix + attr.id + "']")
      element.parent().find(selector_el + ' li:not(:first)').remove()

      el = angular.element(document).find('#' + prefix + attr.id)
      el.attr('ng-model', 'product.attributes[' + attr.id + ']')
      el.attr('ng-options', 'value.title group by value.group for value in product.values[' + attr.id + '] track by value.id')
      el.attr('ng-change', 'last_select_attr=' + attr.id)
      $compile(el)($scope)
      el = element.find('.filter-option')
      el.attr('ng-bind', 'product.attributes[' + attr.id + '].title')
      $compile(el)($scope)
      el = element.parent().find(selector_el + ' li:first')
      el.attr('ng-repeat', 'val in product.values[' + attr.id + ']')
      el.attr('data-original-index', "{{$index}}")
      el.find('a .text').attr('ng-bind', "val.title")
      $compile(el)($scope)
  .error ->
    console.error('An error occurred during submission')

  set_price = () ->
    selected_attributes = []

    angular.forEach attributes, (key) ->
      if $scope.product.attributes[key].id != 0
        selected_attributes.push($scope.product.attributes[key].id)
      #    Todo igor: if selected_attributes is empty - message select - attribute for display price

    exist_selected_attr = clone_data.product_versions[selected_attributes.toString()]

    if exist_selected_attr
      $scope.product.price = clone_data.product_versions[selected_attributes.toString()]
    return exist_selected_attr

  $scope.update_price = () ->
    if not set_price()
      angular.forEach clone_data.variant_attributes[$scope.product.attributes[$scope.last_select_attr].id], (attr) ->
        $scope.product.values[attr.id] = attr.values

        if attr.in_group[1] and attr.in_group[1].first_visible
          $scope.product.attributes[attr.id] = attr.in_group[1]
        else if $scope.product.values[attr.id]
          $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0]

      if not set_price()
        $scope.product.price = clone_data.price

        angular.forEach clone_data.attributes, (attr) ->
          $scope.product.values[attr.id] = attr.values
          $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0]

          if clone_data.product_version_attributes[attr.id]
            $scope.product.attributes[attr.id] = clone_data.product_version_attributes[attr.id]
      console.log('choose the option with the lowest price')
]
