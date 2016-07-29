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

  $http.post($location.absUrl()).success (data) ->
    $scope.options = data.options
    $scope.options_children = data.options_children
    $scope.list_options = data.list_options
    if data.price
      $scope.new_price = data.price
    else
      $scope.product.product_not_availability = data.product_not_availability
    $scope.product_id = data.product_id
    $scope.active = data.active
    $scope.wish_list_url = data.wish_list_url
  .error ->
    console.error('An error occurred during submission')


  $scope.change_price = (option_id) ->
#    if $scope.option_model
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

      angular.element(document.getElementById('options-0')).append $compile('<div id="' + $scope.option_id + '">
                      <select class="form-control" ng-model="option_model[' + $scope.option_id + ']"
                      ng-change="change_price()" ng-options="option for option in options_children[' + $scope.option_id + ']" ></select>
                      </div>')($scope)
      el = angular.element($('[ng-model="' + $scope.option_id + '" '))
      model = el
      el = angular.element(document).find('#tests')
      $scope.test = 12
      el.remove()

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
      selected_attributes.push($scope.product.attributes[key].id)
    $scope.product.price = product_versions[selected_attributes.toString()]
    console.log(product_versions)
    console.log(selected_attributes.toString())

  $scope.change_wishlist = () ->
    if $scope.active !='none'
      $http.post($scope.wish_list_url + 'products/' + $scope.product_id + '/delete/').success (data) ->
        $scope.active = 'none'
      .error ->
        console.error('An error occurred during submission')
    else
      $http.post('/accounts/wishlists/add/' + $scope.product_id + '/').success (data) ->
        $scope.active = 'active'
      .error ->
        console.error('An error occurred during submission')

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

  $http.post($location.absUrl(), {'page': $scope.page_number, 'sorting_type': $scope.sorting_type}).success (data) ->
    items = angular.element(document).find('#product')
    items.attr('ng-repeat', 'product in products')
    $compile(items)($scope)
    clear = angular.element('.clear')
    clear.remove()
    $scope.products = data.products
    $scope.initial_page_number = data.page_number
    $scope.num_pages = data.num_pages
    $scope.pages = [data.pages[parseInt($scope.initial_page_number)-1]]
    $scope.pages[0].active = "True"
    $scope.pages[0].link = ""
    $scope.sorting_type = data.sorting_type
  .error ->
    console.error('An error occurred during submission')

  $scope.submit = () ->
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
