'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module "#{app_name}.controllers"

app.controller 'Catalogue', ['$http', '$scope', '$window', '$document', '$log', 'djangoUrl', ($http, $scope, $window, $document, $log, djangoUrl) ->
  products_url = djangoUrl.reverse('catalogue:products')
  $scope.products_template = 'templates/catalogue/partials/product_json.html'

  $scope.$watch "category", () ->
    $http.post(products_url, {category_pk: $scope.category.pk}).success (products) ->
      $scope.products = products
    .error ->
      console.error('An error occurred during submission')
]