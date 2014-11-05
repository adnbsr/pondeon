'use strict';

var app = angular.module("pondeon", ["ngRoute", "ngMaterial"]);


app.config(['$routeProvider', function($routeProvider) {

    $routeProvider.when('/home', {
        templateUrl: 'static/partials/home.html',
        controller: 'HomeCtrl'
    });

    $routeProvider.otherwise({
        redirectTo: '/home'
    });
}]);

app.controller('HomeCtrl', function($scope) {
    $scope.message = "Pondeon"
});