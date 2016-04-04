'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module "#{app_name}.controllers"

app.controller 'Catalogue', ['$http', '$scope', '$location', '$window', '$document', '$log', 'djangoUrl', ($http, $scope, $location, $window, $document, $log, djangoUrl) ->
  products_url = djangoUrl.reverse('catalogue:products')

#  $scope.$watch "category", () ->
#    $http.post(products_url, {category_pk: $scope.category.pk}).success (data) ->
#      $scope.products = data.products
#      $scope.paginator = data.paginator
#    .error ->
#      console.error('An error occurred during submission')
]