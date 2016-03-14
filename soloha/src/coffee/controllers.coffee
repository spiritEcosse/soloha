'use strict'

### Controllers ###

app_name = "soloha"
app = angular.module "#{app_name}.controllers", []

app.controller 'Header', ['$http', '$scope', '$window', '$document', '$log', 'djangoUrl', ($http, $scope, $window, $document, $log, djangoUrl) ->
  categories = djangoUrl.reverse('promotions:categories')

  $http.post(categories).success (categories) ->
    $scope.categories = categories
  .error ->
    console.log('An error occurred during submission')
]

