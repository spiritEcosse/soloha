'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module app_name, []


app.controller 'Catalogue', ['$http', '$scope', '$location', '$window', '$document', '$log', ($http, $scope, $location, $window, $document, $log) ->
#  products_url = djangoUrl.reverse('catalogue:products')

  $scope.product = 'as'
#  $scope.$watch "category", () ->
#    $http.post(products_url, {category_pk: $scope.category.pk}).success (data) ->
#      $scope.products = data.products
#      $scope.paginator = data.paginator
#    .error ->
#      console.error('An error occurred during submission')
]
