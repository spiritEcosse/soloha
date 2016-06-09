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
  selected_attributes = []
  attributes = []
  product_versions = []

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
        delete $scope.list_options[$scope.option_id]

        angular.element(document.getElementById('options-0')).append $compile('<span id="' + $scope.option_id + '">
                <select class="form-control" ng-model="option_model[' + $scope.option_id + ']"
                ng-change="change_price(option_id)" ng-options="option for option in options_children[' + $scope.option_id + ']" ></select>
                </span>')($scope)
      else
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
    console.log(product_versions)
    console.log(selected_attributes.toString())

]

app.controller 'More_goods', ['$http', '$scope', '$window', '$document', '$location', '$compile', '$routeParams', ($http, $scope, $window, $document, $location, $compile, $routeParams) ->
  getParameterByName = (name, url) ->
    if !url
      url = window.location.href
    name = name.replace(/[\[\]]/g, '\\$&')
    regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)')
    results = regex.exec(url)
    if !results
      return null
    if !results[2]
      return ''
    decodeURIComponent results[2].replace(/\+/g, ' ')

  $scope.sorting_type = '-views_count'
  if getParameterByName('sorting_type')
    $scope.sorting_type = getParameterByName('sorting_type')
  $scope.page_number = '1'
  if getParameterByName('page')
    $scope.page_number = getParameterByName('page')
  console.log($scope.page_number)

  $http.post($location.absUrl(), {'page': $scope.page_number, 'sorting_type': $scope.sorting_type}).success (data) ->
    items = angular.element(document).find('#product')
    items.attr('ng-repeat', 'product in products')
    $compile(items)($scope)
    clear = angular.element('.clear')
    clear.remove()
    $scope.products = data.products
    $scope.initial_page_number = data.page_number
#    $scope.page_number = data.page_number
    $scope.num_pages = data.num_pages
    $scope.pages = [data.pages[parseInt($scope.initial_page_number)-1]]
    $scope.pages[0].active = "True"
    $scope.pages[0].link = ""
    $scope.sorting_type = data.sorting_type
    console.log(data)
  .error ->
    console.error('An error occurred during submission')

  $scope.submit = ->
    $http.post($location.absUrl(), {'page': $scope.page_number, 'sorting_type': $scope.sorting_type}).success (data) ->
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
    .error ->
      console.error('An error occurred during submission')
]
