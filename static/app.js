'use strict';

// Declare app level module which depends on views, and components
angular.module('myApp', [
  'ngRoute',
  'myApp.navbar',
  'myApp.query',
  'myApp.grid',
  'myApp.login',
  'myApp.logout',
  'myApp.version',
  'ngDraggable'
]).
config(['$routeProvider', function($routeProvider) {
  $routeProvider.otherwise({redirectTo: '/query'});
}]);
