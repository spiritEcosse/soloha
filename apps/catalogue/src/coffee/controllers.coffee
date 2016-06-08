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
      el.attr('attr-dis', '1')

      $compile(el)($scope)
  .error ->
    console.error('An error occurred during submission')

  $scope.update_price = (attr_id) ->
    el = angular.element(document).find('#attribute-' + attr_id)

    if el.attr('attr-dis') == '1'
      selected_attributes = []
      angular.forEach attributes, (key) ->
        if $scope.product.attributes[key].id != 0
          selected_attributes.push($scope.product.attributes[key].id)
      #    Todo igor: if selected_attributes is empty - message select - attribute for display price

      if product_versions[selected_attributes.toString()]
        $scope.product.price = product_versions[selected_attributes.toString()]
      else
        angular.forEach clone_data.variant_attributes[$scope.product.attributes[attr_id].id], (attr) ->
          el = angular.element(document).find('#attribute-' + attr.id)
          el.attr('attr-dis', '0')
          $compile(el)($scope)
          $scope.product.values[attr.id] = attr.values

          if attr.in_group[1] and attr.in_group[1].first_visible
            $scope.product.attributes[attr.id] = attr.in_group[1]
          else if $scope.product.values[attr.id]
            $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0]

        angular.forEach attributes, (key) ->
          el = angular.element(document).find('#attribute-' + key)
          el.attr('attr-dis', '1')
          $compile(el)($scope)

        selected_attributes = []
        angular.forEach attributes, (key) ->
          if $scope.product.attributes[key].id != 0
            selected_attributes.push($scope.product.attributes[key].id)

        if product_versions[selected_attributes.toString()]
          $scope.product.price = product_versions[selected_attributes.toString()]
        else
          $scope.product.price = clone_data.price

          angular.forEach clone_data.attributes, (attr) ->
            $scope.product.values[attr.id] = attr.values
            $scope.product.attributes[attr.id] = $scope.product.values[attr.id][0]

            if clone_data.product_version_attributes[attr.id]
              $scope.product.attributes[attr.id] = clone_data.product_version_attributes[attr.id]
]
