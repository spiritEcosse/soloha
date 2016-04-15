'use strict'

### Controllers ###

app_name = 'soloha'
app = angular.module app_name, ['ngResource']

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]

app.factory 'Product', ['$resource', ($resource) ->
    $resource '/catalogue/crud/product/', { 'pk': '@pk' }, {}
]

app.controller 'Product', ['$http', '$scope', '$window', '$document', '$location', 'Product', ($http, $scope, $window, $document, $location, Product) ->
#  $scope.product = Product.get({pk: 3})
#  console.log($scope.product)
  $scope.data = {}
  $scope.product = Product.query()
  $scope.product.$promise.then (results) ->
      console.log(Product.query(pk: 1))
  
  
#  $scope.photos = {}
#  $scope.posts = Post.query()
#  $scope.posts.$promise.then (results) ->
#       Load the photos
#      angular.forEach results, (post) ->
#          $scope.photos[post.id] = PostPhoto.query(post_id: post.id)
#  console.log(Product.get(pk: 1))
  
#  product.$promise.then (product) ->
#  console.log product

  $http.post($location.absUrl()).success (data) ->
    console.log(data)
  .error ->
    console.error('An error occurred during submission')
]
