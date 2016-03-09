'use strict'

### Declare app level module which depends on filters, and services ###

app_name = 'soloha'
app = angular.module app_name, ["#{app_name}.controllers", 'ng.django.urls']

app.config ['$httpProvider', ($httpProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
]