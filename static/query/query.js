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

.controller('QueryCtrl', ['$scope', '$http', 'ngDialog', 'ExcelService', 'RentrakService',
    function($scope, $http, ngDialog, ExcelService, RentrakService) {
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
      $scope.metrics = [];
      $scope.metrics_chosen = [];

      $scope.gatheringInfo = false;
      $scope.errorResponse = false;

      $scope.init = function() {
        $http.get('/getMetrics/').then(function(res){
            var metrics = res.data;

            angular.forEach(metrics, function(metric) {
                if($scope.metrics.length == 0){
                    $scope.metrics.push(metric);
                }else{
                    var doInsert = true;

                    for(var i = 0; i < $scope.metrics.length; i++) {
                        if($scope.metrics[i].id == metric.id) {
                            doInsert = false;
                            break;
                        }
                    }

                    if(doInsert){
                        $scope.metrics.push(metric);
                    }
                }
            });

            $scope.initiated = true;
        });
      };

      $scope.query = function() {
        var params = {};
        params.brand_id = $scope.brand_id;
        params.ad_id = $scope.ad_id;
        params.st_week_id = $scope.st_week_id;
        params.end_week_id = $scope.end_week_id;
        params.deal_id = $scope.deal_id;

        $scope.errorResponse = false;
        $scope.gatheringInfo = true;
        $scope.gatheringStatus = 'Querying On-Air as-run logs';

        $http.post('/queryWithParams/', {params: params}).then(function(res){
            $scope.results = res.data;
            $scope.gatheringStatus = 'Querying Rentrak API';

            var rows_done = 0;

            angular.forEach($scope.results, function(row, index){
                RentrakService.getRentrakData(row.PROPERTY_NAME, row.AIR_DTTM, row.UNIT_LENGTH, $scope.metrics_chosen)
                .then(function(rows){
                    rows_done++;

                    angular.forEach($scope.metrics_chosen, function(metric) {
                        row[metric] = rows[0][metric];
                    });

                    row.PROPERTY_NAME = row.PROPERTY_NAME + '/' + rows[0].network_name;

                    if(rows_done == $scope.results.length)
                    {
                        $scope.gatheringInfo = false;
                        $scope.gatheringStatus = '';
                    }
                },function(res){
                    $scope.gatheringInfo = false;
                    $scope.gatheringStatus = '';

                    $scope.errorResponse = true;
                    $scope.errorMessage = 'Error: ' + res.data
                });
            });
        },function(res){
            $scope.errorMessage = 'Error: ' + res.data
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

      $scope.onMetricSelect = function() {
        $scope.metrics_chosen = [];

        $scope.metrics.map(function(metric){
            if(metric.selected){
                $scope.metrics_chosen.push(metric.name);
            }
        });
      }

      $scope.exportToExcel=function(tableId){
        ExcelService.tableToExcel(tableId, 'Data Fetcher');
      };

      $scope.init();
}]);