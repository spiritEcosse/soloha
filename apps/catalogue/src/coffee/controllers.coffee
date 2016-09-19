'use strict'

### Controllers ###

app_name = 'soloha'
app = angular.module app_name


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


app.controller 'Product', ['$http', '$scope', '$window', '$document', '$location', '$compile', '$filter', 'djangoForm', '$rootScope', 'djangoUrl', ($http, $scope, $window, $document, $location, $compile, $filter, djangoForm, $rootScope, djangoUrl) ->
    $scope.product = []
    $scope.product.values = []
    $scope.product.attributes = []
    $scope.attributes = []
    attributes = []
    clone_data = null
    $scope.last_select_attr = null
    $scope.isOpen = []
    $scope.product.custom_values = []
    $scope.product.custom_value = []
    $scope.product.dict_attributes = []
    $scope.query_attr = []
    $scope.send_form = false
    $scope.alert_mode = 'success'
    $scope.prod_images = []
    $scope.product_primary_images = []
    $scope.product_images = null
    $rootScope.Object = Object
    $rootScope.keys = Object.keys
    $scope.sent_signal = []
    clone_attributes = []

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

    $http.post($location.absUrl()).success (data) ->
        clone_data = data
        $scope.options = data.options
        $scope.options_children = data.options_children
        $scope.list_options = data.list_options
        $scope.attributes = data.attributes
        angular.copy(data.attributes, clone_attributes)

        $scope.product = data.product
        $scope.product.custom_values = $scope.isOpen = $scope.product.dict_attributes = $scope.product.custom_value = []

        angular.forEach $scope.attributes, (attr) ->
            attributes.push(attr.pk)

            if attr.selected_val.images.length
                $scope.product_images = pk: attr.selected_val.images[0].pk

            $scope.product.dict_attributes[attr.pk] = attr
            $scope.product.custom_value[attr.pk] = null
            $scope.isOpen[attr.pk] = false
            $scope.product.custom_values[attr.pk] = []
        $scope.price_start = set_price()
    .error ->
        console.error('An error occurred during submission')

    $scope.update_price_with_custom_val = (attr_pk, value) ->
        if value?
            $scope.product.attributes[attr_pk] = value
        else
            $scope.product.attributes[attr_pk] = $scope.product.custom_value[attr_pk]

        selected_attributes = []

        angular.forEach clone_data.attributes, (attr) ->
            non_standard = $scope.product.dict_attributes[attr.pk].non_standard

            if $scope.product.attributes[attr.pk].pk != 0 and non_standard is true
                selected_attributes.push($scope.product.attributes[attr.pk])

        if selected_attributes.length
            $http.post('/catalogue/calculate/price/' + clone_data.product.pk, {'selected_attributes': selected_attributes, 'current_attr': $scope.product.attributes[attr_pk]}).success (data) ->
                if not data.error?
                    $scope.price = data.price

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

    get_prod = (selected_val) ->
        if selected_val.products? and not selected_val.products.length or not selected_val.products?
            $http.post('/catalogue/attr/' + selected_val.pk + '/product/' + clone_data.product.pk + '/').success (data) ->
                selected_val.products = data.products

                if data.product_primary_images.length and not selected_val.images?
                    $scope.product_images = pk: data.product_primary_images[0].pk

                selected_val.images = data.product_primary_images
            .error ->
                console.error('An error occurred during submission')

    $scope.attr_prod = (value) ->
        get_prod(value)

    $scope.attr_prod_images = (value, product) ->
        if product.images? and not product.images.length
            product.sent_signal = true

            $http.post('/catalogue/attr/product/' + product.pk  + '/images/').success (data) ->
                product.sent_signal = false
                images = data.images

                if not data.images.length
                    images = null
                product.images = images
            .error ->
                console.error('An error occurred during submission')

    set_price = () ->
        selected_attributes = []

        attributes = $filter('orderBy')($scope.attributes, 'pk')

        angular.forEach attributes, (attribute) ->
            if attribute.selected_val.pk != 0
                console.log(attribute.selected_val)
                selected_attributes.push(attribute.selected_val.pk)
        #    Todo igor: if selected_attributes is empty - message select - attribute for display price

        exist_selected_attr = clone_data.stockrecords[selected_attributes.toString()]

        console.log(selected_attributes)

        if exist_selected_attr
            $scope.price = exist_selected_attr.price
            $scope.stockrecord = exist_selected_attr.stockrecord_id
            return exist_selected_attr.price

        return false

    $scope.update_price = (value, current_attribute) ->
        current_attribute.selected_val = value
        get_prod(value)

        angular.forEach clone_data.variant_attributes[value.pk], (attr) ->
            attribute = $filter('filter')($scope.attributes, { pk: attr.pk })[0]
            attribute.values = attr.values

        if not set_price()
            angular.forEach clone_data.variant_attributes[value.pk], (attr) ->
                attribute = $filter('filter')($scope.attributes, { pk: attr.pk })[0]
                attribute.values = attr.values

                # remove from if  -- and attr.values[1].visible

                if attr.values[1] and attr.values[1].visible
                    attribute.selected_val = attr.values[1]
                else if attribute.values
                    attribute.selected_val = attribute.values[0]

                console.log('variant_attributes', attribute.selected_val)
                get_prod(attribute.selected_val)

            if not set_price()
                $scope.price = $scope.price_start

                angular.forEach $scope.attributes, (attr) ->
                    attribute = $filter('filter')(clone_attributes, { pk: attr.pk })[0]
                    attr.values = attribute.values
                    attr.selected_val = attribute.selected_val
                    get_prod(attribute.selected_val)

    $scope.quick_order = () ->
        if $scope.quick_order_data
            $http.post('/catalogue/quick/order/' + clone_data.product.pk, $scope.quick_order_data).success((out_data) ->
                if !djangoForm.setErrors($scope.quick_order_form, out_data.errors)
                    $scope.send_form = true
            ).error ->
                console.error 'An error occured during submission'

    $scope.change_wishlist = () ->
        if $scope.active !='none'
            $http.post($scope.wish_list_url + 'products/' + $scope.product_id + '/delete/').success (data) ->
                $scope.active = 'none'
            .error ->
                console.error('An error occurred during submission')
        else
            $http.post('/accounts/wishlists/add/' + $scope.product_id + '/').success (data) ->
                $scope.active = "active"
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
