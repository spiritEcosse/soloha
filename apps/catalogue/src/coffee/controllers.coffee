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

app.filter 'search_by_title', ->
    (list, needle) ->
        if list and needle
            return if needle in [val.title for val in list][0] then true else false
        return null

app.filter 'filter_attribute', ->
    (list, needle) ->
        if list and needle? and needle != ''
            needle = needle.toString()
            new_list = [val for val in list when val.title.toString().indexOf(needle) > -1]
            return if new_list.length then new_list else false
        return list

app.directive 'focusMe', ($timeout, $parse) ->
    { link: (scope, element, attrs) ->
        model = $parse(attrs.focusMe)
        scope.$watch model, (value) ->
            if value == true
                $timeout ->
                    element[0].focus()
                    return
            return
        element.bind 'blur', ->
            scope.$apply model.assign(scope, false)
            return
        return
    }

app.controller 'Product', ['$http', '$scope', '$window', '$document', '$location', '$compile', '$filter', ($http, $scope, $window, $document, $location, $compile, $filter) ->
    $scope.product = []
    $scope.product.values = []
    $scope.product.attributes = []
    attributes = []
    clone_data = null
    $scope.last_select_attr = null
    prefix = 'attribute-'
    selector_el = '.dropdown-menu.inner'
    $scope.isOpen = []
    $scope.product.custom_values = []
    $scope.product.custom_value = []
    $scope.product.dict_attributes = []
    $scope.product.query_attr = []

    $scope.change_price = (option_id) ->
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
        clone_data = data
        $scope.options = data.options
        $scope.options_children = data.options_children
        $scope.list_options = data.list_options

        if data.price
            $scope.product.price = data.price
            el = angular.element('#product_price')
            el.attr('ng-bind', 'product.price')
        else
            $scope.product.product_not_availability = data.product_not_availability
            el = angular.element('#product_not_availability')
            el.attr('ng-bind', 'product.product_not_availability')
        $compile(el)($scope)

        angular.forEach data.attributes, (attr) ->
            attributes.push(attr.pk)
            $scope.product.values[attr.pk] = attr.values
            $scope.product.dict_attributes[attr.pk] = attr
            $scope.product.attributes[attr.pk] = $scope.product.values[attr.pk][0]
            $scope.product.custom_value[attr.pk] = null
            $scope.isOpen[attr.pk] = false
            $scope.product.custom_values[attr.pk] = []

            if data.product_version_attributes[attr.pk]
                $scope.product.attributes[attr.pk] = data.product_version_attributes[attr.pk]

            element = angular.element(document).find("[data-id='" + prefix + attr.pk + "']")
            element.parent().find(selector_el + ' li:not(:first)').remove()

            dropdown = angular.element(document).find('#' + prefix + attr.pk)
            dropdown.attr('ng-click', "click_dropdown(" + attr.pk + ", $event)")
            dropdown.find('button .title').attr('ng-bind', 'product.attributes[' + attr.pk + '].title')
            dropdown.find('button .attr-pk').attr('ng-bind', 'product.attributes[' + attr.pk + '].pk')
            dropdown.find('form').attr('name', 'attr_form[' + attr.pk + ']')
            dropdown_menu = dropdown.find('.dropdown-menu')
            dropdown_menu.find('li.list:not(:first)').remove()
            li = dropdown_menu.find('li.list')
            li.attr('data-original-index', '{{$index}}')
            li.find('a').attr('ng-click', 'update_price($index, "' + attr.pk + '")').html("{{value.title}}")
            li.find('a').attr('href', "#")
            li.attr('ng-repeat', 'value in product.values[' + attr.pk + '] | filter: {title: query_attr[' + attr.pk + ']}')
            li.attr('ng-class', '{"selected active": value.pk == product.attributes[' + attr.pk + '].pk}')
            dropdown_menu.find('.divider').attr('ng-if', 'product.custom_values[' + attr.pk + '].length || product.custom_value[' + attr.pk + '] !== null')
            input = dropdown_menu.find('input')
            input.attr('ng-model', "query_attr[" + attr.pk + "]")
            custom_value_li = dropdown_menu.find('li.query')
            custom_value_li.attr('ng-if', '(product.custom_values[' + attr.pk + '] | search_by_title: product.custom_value[' + attr.pk + '].title) == false')
            custom_values_li = dropdown_menu.find('li.custom')
            custom_values_li.attr('ng-if', 'product.custom_values[' + attr.pk + '].length')

            if attr.non_standard is true and clone_data.product.non_standard_price_retail != 0
                input.attr('min', attr.bottom_line).attr('max', attr.top_line)
                input.attr('ng-change', "search(" + attr.pk + ")")
                custom_value_li.find('a').attr('ng-click', 'update_price_with_custom_val(' + attr.pk + ')').html('{{product.custom_value[' + attr.pk + '].title}}')
                custom_values_li.attr('ng-repeat', 'value in product.custom_values[' + attr.pk + '] | filter:{title: query_attr[' + attr.pk + ']} | orderBy: "title" track by $index')
                custom_values_li.attr('ng-class', '{"selected active": value.title == product.attributes[' + attr.pk + '].title}')
                custom_values_li.find('a').attr('ng-click', 'update_price_with_custom_val(' + attr.pk + ', $index)').html('{{value.title}}')

            $compile(custom_values_li)($scope)
            $compile(custom_value_li)($scope)
            $compile(dropdown)($scope)
            $compile(input)($scope)
            $compile(li)($scope)
    .error ->
        console.error('An error occurred during submission')

    $scope.update_price_with_custom_val = (attr_pk, index = null) ->
        if index?
            $scope.product.attributes[attr_pk] = $scope.product.custom_values[attr_pk][index]
        else
            $scope.product.attributes[attr_pk] = $scope.product.custom_value[attr_pk]

        selected_attributes = []

        angular.forEach clone_data.attributes, (attr) ->
            non_standard = $scope.product.dict_attributes[attr.pk].non_standard

            if $scope.product.attributes[attr.pk].pk != 0 and non_standard is true
                selected_attributes.push($scope.product.attributes[attr.pk])

        if selected_attributes.length
            $http.post('/catalogue/calculate/price/' + clone_data.product.pk, {'selected_attributes': selected_attributes, 'current_attr': $scope.product.custom_value[attr_pk]}).success (data) ->
                if not data.error?
                    $scope.product.price = data.price

                    if $scope.product.custom_value[attr_pk] and not $filter('search_by_title')($scope.product.custom_values[attr_pk], $scope.product.custom_value[attr_pk].title)
                        $scope.product.custom_values[attr_pk].push($scope.product.custom_value[attr_pk])
                else
                    for key, value of data.error
                        $scope.product.attributes[key].error = value
            .error ->
                console.error('An error occurred during submission')

    $scope.search = (attr_pk) ->
        if $scope.query_attr[attr_pk]? and $scope.query_attr[attr_pk] != '' and not $filter('search_by_title')($scope.product.custom_values[attr_pk], $scope.query_attr[attr_pk])
            $scope.product.custom_value[attr_pk] = {'pk': -1, 'title': $scope.query_attr[attr_pk], 'parent': attr_pk}
        else
            $scope.product.custom_value[attr_pk] = null

    $scope.click_dropdown = (attr_id) ->
#Todo bug with focus. If click on button three times, open dropdown without focus on us input.
        $scope.isOpen[attr_id] = if $scope.isOpen[attr_id] is false then true else false

    set_price = () ->
        selected_attributes = []

        angular.forEach attributes, (key) ->
            if $scope.product.attributes[key].pk != 0
                selected_attributes.push($scope.product.attributes[key].pk)
        #    Todo igor: if selected_attributes is empty - message select - attribute for display price

        exist_selected_attr = clone_data.product_versions[selected_attributes.toString()]

        if exist_selected_attr
            $scope.product.price = exist_selected_attr
        return exist_selected_attr

    $scope.update_price = (index, attr_pk) ->
        if $scope.product.values[attr_pk][index]
            $scope.product.attributes[attr_pk] = $scope.product.values[attr_pk][index]

        angular.forEach clone_data.variant_attributes[$scope.product.attributes[attr_pk].pk], (attr) ->
            $scope.product.values[attr.pk] = attr.values

        if not set_price()
            angular.forEach clone_data.variant_attributes[$scope.product.attributes[attr_pk].pk], (attr) ->
                $scope.product.values[attr.pk] = attr.values

                if attr.in_group[1] and attr.in_group[1].visible
                    $scope.product.attributes[attr.pk] = attr.in_group[1]
                else if $scope.product.values[attr.pk]
                    $scope.product.attributes[attr.pk] = $scope.product.values[attr.pk][0]

            if not set_price()
                $scope.product.price = clone_data.price
                selected_attributes = []

                angular.forEach clone_data.attributes, (attr) ->
                    $scope.product.values[attr.pk] = attr.values
                    $scope.product.attributes[attr.pk] = $scope.product.values[attr.pk][0]

                    if clone_data.product_version_attributes[attr.pk]
                        $scope.product.attributes[attr.pk] = clone_data.product_version_attributes[attr.pk]

                    if $scope.product.attributes[attr.pk].pk != 0
                        selected_attributes.push($scope.product.attributes[attr.pk].pk)

    $scope.quick_order = () ->
        console.log($scope.subscribe_data)

        if $scope.subscribe_data
            $http.post('/catalogue/quick/order/' + clone_data.product.pk, $scope.subscribe_data).success((out_data) ->
                if !djangoForm.setErrors($scope.my_form, out_data.errors)
                    $window.location.href = out_data.success_url
                return
            ).error ->
                console.error 'An error occured during submission'
                return
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

    $scope.click_test_option = ->
        console.log('hello')
]
