'use strict'

describe 'Catalogue', () ->
  beforeEach(module('soloha'))
  $controller = undefined

  beforeEach inject (_$controller_) ->
    $controller = _$controller_

  it 'should change price by attribute', () ->
    $scope = {}
    controller = $controller 'Catalogue', { $scope: $scope }
    expect($scope.product).toEqual('as')

