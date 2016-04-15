'use strict'

describe 'Catalogue', () ->
  beforeEach(module('soloha'))
  $controller = undefined

  beforeEach inject (_$controller_) ->
    $controller = _$controller_

  it 'should change price by attribute', () ->
    $scope = {}
    controller = $controller 'Product', { $scope: $scope}
    console.log($scope.pk)
    
    $scope.product.$promise.then (product) ->
      console.log($scope.product.pk)
      
#    console.log($scope.product.pk)
#    expect(scope.product).toEqual(Product.get({pk: 1}))

  