'use strict';

angular.module('myApp.query', ['ngRoute', 'ui.bootstrap', 'ngDialog', 'ServicesModule'])

.config(['$routeProvider', 'ngDialogProvider', '$locationProvider', function($routeProvider, ngDialogProvider, $locationProvider) {
  $routeProvider.when('/query', {
    templateUrl: 'static/query/query.html',
    controller: 'QueryCtrl'
  });

  ngDialogProvider.setDefaults({
    className: 'ngdialog-theme-plain',
    showClose: true,
    closeByDocument: true,
    closeByEscape: true
  });

  $locationProvider.html5Mode(true);
}])

.controller('QueryCtrl', ['$scope', '$http', 'ngDialog', 'ExcelService',
    function($scope, $http, ngDialog, ExcelService) {
      $scope.initiated = false;
      $scope.brand_id = '';
      $scope.ad_id = '';
      $scope.deal_id = '';
      $scope.st_week_id = '';
      $scope.end_week_id = '';
      $scope.ad_name = '';
      $scope.brand_name = '';
      $scope.deal_name = '';
      $scope.results = [];

      $scope.init = function() {
        $scope.initiated = true;
      };

      $scope.query = function() {
        var params = {};
        params.brand_id = $scope.brand_id;
        params.ad_id = $scope.ad_id;
        params.st_week_id = $scope.st_week_id;
        params.end_week_id = $scope.end_week_id;
        params.deal_id = $scope.deal_id;

        $http.post('/queryWithParams/', {params: params}).then(function(res){
            $scope.results = res.data;
        });
      }

      $scope.getAdvertiser = function(search) {
        return $http.post('/findAdvertisers/', {search: search}).then(function(res){
            return res.data.map(function(ad){
                return ad;
              });
        });
      };

      $scope.getBrand = function(search) {
        return $http.post('/findBrands/', {search: search}).then(function(res){
            return res.data.map(function(b){
                return b;
              });
        });
      };

      $scope.getDeal = function(search) {
        return $http.post('/findDeals/', {search: search}).then(function(res){
            return res.data.map(function(d){
                return d;
              });
        });
      };

      $scope.onAdSelect = function($item, $model, $label, $event) {
        $scope.ad_id = $item.ADVERTISER_ID;
        $scope.ad_name = $item.ADVERTISER_NAME;
      }

      $scope.onBrandSelect = function($item, $model, $label, $event) {
        $scope.brand_id = $item.BRAND_ID;
        $scope.brand_name = $item.BRAND_NAME;
      }

      $scope.onDealSelect = function($item, $model, $label, $event) {
        $scope.deal_id = $item.DEAL_ID;
        $scope.deal_name = $item.DEAL_NAME;
      }

      $scope.exportToExcel=function(tableId){
        ExcelService.tableToExcel(tableId, 'Data Fetcher');
      };

      $scope.init();
}]);