'use strict'

### Controllers ###

app_name = 'soloha'
#app = angular.module app_name, ['ngResource']
app = angular.module app_name

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

#  $scope.new_price = 1

  $http.post($location.absUrl()).success (data) ->
    $scope.options = data.options
    $scope.options_children = data.options_children
    $scope.list_options = data.list_options
    if data.price
      $scope.new_price = data.price
    else
      $scope.product.product_not_availability = data.product_not_availability
  .error ->
    console.error('An error occurred during submission')


  $scope.change_price = (option_id) ->
#    if $scope.option_model
    console.log(option_id)
    if Object.keys($scope.options_children).length != 0 # && Object.keys($scope.options_children[$scope.option_id]).length != 0
      $scope.option_id = Object.keys($scope.options_children[$scope.option_id]).filter((key) ->
        $scope.options_children[$scope.option_id][key] == $scope.option_model[$scope.option_id]
      )[0]
    else if $scope.option_id
      $scope.option_id = $scope.model[$scope.option_id]
    else
      $scope.option_id = $scope.model[0]
    if $scope.options[$scope.option_id]
      $scope.new_price += parseFloat($scope.options[$scope.option_id])
    else
      $scope.parent = true

    $http.post($location.absUrl(), {'option_id': $scope.option_id, 'parent': $scope.parent, 'list_options': $scope.list_options}).success (data) ->
      $scope.options = data.options #
      $scope.options_children[$scope.option_id] = data.options_children

      if Object.keys($scope.options_children[$scope.option_id]).length != 0
#        console.log(data.options_children)
        delete $scope.list_options[$scope.option_id]

        angular.element(document.getElementById('options-0')).append $compile('<span id="' + $scope.option_id + '">
                <select class="form-control" ng-model="option_model[' + $scope.option_id + ']"
                ng-change="change_price(option_id)" ng-options="option for option in options_children[' + $scope.option_id + ']" ></select>
                </span>')($scope)
      else
        console.log("new")
        delete $scope.list_options[$scope.option_id]
        #           $scope.current_model = $scope.model[$scope.option_id]
        angular.element(document.getElementById('options-0')).append $compile('<div id="model[' + $scope.option_id + ']">
              <select class="form-control" ng-model="option_model[' + $scope.option_id + ']"
              ng-change="change_price(option_id)" ng-options="option for option in list_options" ></select>
              </div>')($scope)
    .error ->
      console.error('An error occurred during submission')


      angular.element(document.getElementById('options-0')).remove(ng-model="option_model[' + $scope.option_id + ']")

      angular.forEach data.attributes, (attr) ->
      el = angular.element($('[ng-model="option_model[' + 69 + ']" '))
      el.remove()
      el = angular.element($('[ng-model="option_model[' + $scope.option_id + ']"'))
      el = angular.element($('[ng-model="confirmed"'))
      console.log(el.find('div').remove())

      angular.element(document.getElementById('options-0')).append $compile('<div id="' + $scope.option_id + '">
                      <select class="form-control" ng-model="option_model[' + $scope.option_id + ']"
                      ng-change="change_price()" ng-options="option for option in options_children[' + $scope.option_id + ']" ></select>
                      </div>')($scope)
      console.log(this.find('div'))
      el = angular.element($('[ng-model="' + $scope.option_id + '" '))
      model = el
      console.log(model)
      console.log($scope.model)
      el = angular.element(document).find('#tests')
      $scope.test = 12
      console.log($scope.test)
      el.remove()
      console.log($scope.test)

      angular.element(document.getElementById('options-0')).append $compile('<select class="form-control" ng-model="option_model[' + $scope.option_id + ']"
                                                ng-change="change_price()" ng-options="option for option in options_children[' + $scope.option_id + ']" ></select>')($scope)



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
