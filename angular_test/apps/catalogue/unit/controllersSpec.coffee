'use strict'

describe 'Catalogue', () ->
  beforeEach(module('soloha'))
  $controller = undefined

  beforeEach inject (_$controller_, $injector) ->
    $controller = _$controller_
    Product = $injector.get('Product')

  it 'should change price by attribute', inject (Product) ->
    $scope = {}

    product = Product.get(pk: 1)
    product.$promise.then (data) ->
          product.pk = data.pk

#    console.log(product.pk)
    controller = $controller 'Product', { $scope: $scope }
    expect($scope.product.pk).toEqual(product.pk)


  