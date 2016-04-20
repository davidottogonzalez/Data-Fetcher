'use strict';

angular.module('myApp.grid', ['ngRoute', 'ui.bootstrap', 'ngDialog', 'ServicesModule'])

.config(['$routeProvider', 'ngDialogProvider', '$locationProvider', function($routeProvider, ngDialogProvider, $locationProvider) {
  $routeProvider.when('/grid', {
    templateUrl: 'static/grid/grid.html',
    controller: 'GridCtrl'
  });

  ngDialogProvider.setDefaults({
    className: 'ngdialog-theme-plain',
    showClose: true,
    closeByDocument: true,
    closeByEscape: true
  });

  $locationProvider.html5Mode(true);
}])

.controller('GridCtrl', ['$scope', '$http', 'ngDialog', 'ExcelService', 'RentrakService',
    function($scope, $http, ngDialog, ExcelService, RentrakService) {
      $scope.initiated = false;
      $scope.dayparts = [
        {
            id: 1,
            name: 'Daytime'
        },
        {
            id: 2,
            name: 'Early Fringe'
        },
        {
            id: 3,
            name: 'Prime Access'
        },
        {
            id: 4,
            name: 'Prime'
        },
        {
            id: 5,
            name: 'Late Fringe'
        },
        {
            id: 6,
            name: 'Overnight'
        },
        {
            id: 7,
            name: 'Early Morning'
        }
      ];
      $scope.networks = [
        {
            id: 367,
            name: 'Bravo'
        },
        {
            id: 2073,
            name: 'Chiller'
        },
        {
            id: 623,
            name: 'CNBC'
        },
        {
            id: 381,
            name: 'E!'
        },
        {
            id: 8096,
            name: 'Esquire'
        },
        {
            id: 311,
            name: 'Golf'
        },
        {
            id: 357,
            name: 'MSNBC'
        },
        {
            id: 5,
            name: 'NBC'
        },
        {
            id: 7438,
            name: 'NBCSN'
        },
        {
            id: 337,
            name: 'Oxygen'
        },
        {
            id: 377,
            name: 'Syfy'
        },
        {
            id: 383,
            name: 'USA'
        }
      ];
      $scope.day_date = '';
      $scope.chosen_target = '';

      $scope.gatheringInfo = false;
      $scope.errorResponse = false;

      $scope.init = function() {
        $scope.initiated = true;
      };

      $scope.getTag = function(search) {
        return $http.post('/findTags/', {search: search}).then(function(res){
            return res.data.map(function(t){
                return t;
              });
        });
      };

      $scope.onTagSelect = function($item, $model, $label, $event) {
        $scope.chosen_target = $item;
      };

      $scope.getGrid = function() {
        $scope.errorResponse = false;
        $scope.gatheringInfo = true;
        $scope.gatheringStatus = 'Querying Rentrak API';

        RentrakService.getRentrakGridData($scope.networks, $scope.day_date, '')
        .then(function(full_rows){
            RentrakService.getRentrakGridData($scope.networks, $scope.day_date, $scope.chosen_target)
            .then(function(tag_rows){
                $scope.buildGridVars(full_rows, '');
                $scope.buildGridVars(tag_rows, 'tag_');

                $scope.gatheringInfo = false;
                $scope.gatheringStatus = '';
            },function(res){
                $scope.gatheringInfo = false;
                $scope.gatheringStatus = '';

                $scope.errorResponse = true;
                $scope.errorMessage = 'Error: ' + res.data
            });
        });
      };

      $scope.buildGridVars = function(rows, pre){
        angular.forEach($scope.networks, function(network, index){
            angular.forEach(rows, function(row){
                if(row.network_id == network.id){
                    $scope.networks[index][pre + row.local_daypart_name] = {};
                    $scope.networks[index][pre + row.local_daypart_name].reach_live = Math.round(row.reach_live);
                    $scope.networks[index][pre + row.local_daypart_name].reach_dvr_same_day = Math.round(row.reach_dvr_same_day);
                    $scope.networks[index][pre + row.local_daypart_name].reach_live_plus_dvr_same_day = Math.round(row.reach_live_plus_dvr_same_day);
                }
            });
        });
      };

      $scope.exportToExcel=function(tableId){
        ExcelService.tableToExcel(tableId, 'Data Fetcher');
      };

      $scope.init();
}]);