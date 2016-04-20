'use strict';

angular.module('myApp.navbar', [])

.controller('NavbarCtrl', ['$scope', '$http', '$location',
    function($scope, $http, $location) {
        $scope.isLoggedIn = false;
        $scope.isAdmin = false;
        $scope.username = '';

        $scope.tabs = [{
            title: 'Query',
            url: '/query'
        },
        {
            title: 'Audience Grid',
            url: '/grid'
        }];

        $scope.adminTabs = [];

        $scope.currentTab = $location.path() != '/' ? $location.path() : '/query';

        $scope.isActiveTab = function(tabUrl) {
            return tabUrl == $scope.currentTab;
        };

        $scope.onClickTab = function (tab) {
            $scope.currentTab = tab.url;
            $location.path(tab.url);
        };

        $scope.init = function(){
           $http.get('/isUserAuthenticated')
           .then(function(res){
                if(res.data.status)
                {
                    $scope.isLoggedIn = true;
                    $scope.username = res.data.username
                }else
                {
                    $scope.isLoggedIn = false;
                }
           });

           $http.get('/isUserAdmin')
           .then(function(res){
                if(res.data.status)
                {
                    $scope.isUserAdmin = true;
                }else
                {
                    $scope.isUserAdmin = false;
                }
           });
        };

        $scope.init();
    }
]);