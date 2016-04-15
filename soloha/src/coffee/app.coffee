'use strict'

### Declare app level module which depends on filters, and services ###

app_name = 'soloha'
app = angular.module app_name, ['ng.django.urls', 'ui.bootstrap']

app.config ['$httpProvider', '$locationProvider', ($httpProvider, $locationProvider) ->
  $httpProvider.defaults.xsrfCookieName = 'csrftoken'
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
  $locationProvider.html5Mode({
    enabled:true,
    requireBase: false
  })
  $locationProvider.hashPrefix('!')
]
