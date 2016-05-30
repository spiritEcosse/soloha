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
  clone_data = null
  auto_change = false

  $http.post($location.absUrl()).success (data) ->
    clone_data = data
    if data.price
      $scope.product.price = data.price
    else
      $scope.product.product_not_availability = data.product_not_availability
    product_versions = data.product_versions

    angular.forEach data.attributes, (attr) ->
      attributes.push(attr.id)
      $scope.product.values[attr.id] = attr.values
      $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0]

      if data.product_version_attributes[attr.id]
        $scope.product.attributes[attr.id] = data.product_version_attributes[attr.id]

      el = angular.element(document).find('#attribute-' + attr.id)
      el.attr('ng-model', 'product.attributes[' + attr.id + ']')
      el.attr('ng-options', 'value.title group by value.group for value in product.values[' + attr.id + '] track by value.id')
      el.attr('ng-change', 'update_price(' + attr.id + ')')
      el.attr('md-on-open', 'enable_select(' + attr.id + ')')
      el.attr('attr-dis', '1')

      $compile(el)($scope)
  .error ->
    console.error('An error occurred during submission')

  $scope.enable_select = (attr_id) ->
    el = angular.element(document).find('#attribute-' + attr_id)
    el.attr('attr-dis', '1')
    $compile(el)($scope)

  $scope.update_price = (attr_id) ->
    el = angular.element(document).find('#attribute-' + attr_id)

    if el.attr('attr-dis') != '0'
      selected_attributes = []
      angular.forEach attributes, (key) ->
        if $scope.product.attributes[key].id != 0
          selected_attributes.push($scope.product.attributes[key].id)
      #    Todo igor: if selected_attributes is empty - message select - attribute for display price

      if selected_attributes.toString() in product_versions
        $scope.product.price = product_versions[selected_attributes.toString()]
      else
        angular.forEach clone_data.variant_attributes[$scope.product.attributes[attr_id].id], (attr) ->
          console.log(attr.id)
          el = angular.element(document).find('#attribute-' + attr.id)
          el.attr('attr-dis', '0')
          $compile(el)($scope)
          $scope.product.values[attr.id] = attr.values

          if $scope.product.values[attr.id]
            $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0]

          if attr.in_group[1]
            $scope.product.attributes[attr.id] = attr.in_group[1]

        el = angular.element(document).find('#attribute-' + attr_id)
        el.attr('attr-dis', '1')
        $compile(el)($scope)

        selected_attributes = []
        angular.forEach attributes, (key) ->
          if $scope.product.attributes[key].id != 0
            selected_attributes.push($scope.product.attributes[key].id)

        console.log(selected_attributes)
        if selected_attributes.toString() in product_versions
          $scope.product.price = product_versions[selected_attributes.toString()]
          console.log($scope.product.price)
]
