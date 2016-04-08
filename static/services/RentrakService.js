angular.module('ServicesModule').factory('RentrakService', ['$http',
    function($http){

    var getRentrakData = function(network, startTimestamp, unitLength, metricsList){

        startTimeObj = new Date(startTimestamp);
        endTimeObj = new Date(startTimestamp);
        endTimeObj.setSeconds(endTimeObj.getSeconds() + parseInt(unitLength) + 1);

        stringStart = startTimeObj.getFullYear() + '-' + addZero(startTimeObj.getMonth() + 1) + '-' + addZero(startTimeObj.getDate())
                      + 'T' + addZero(startTimeObj.getHours()) + ":" + addZero(startTimeObj.getMinutes()) + ":" + addZero(startTimeObj.getSeconds())

        stringEnd = endTimeObj.getFullYear() + '-' + addZero(endTimeObj.getMonth() + 1) + '-' + addZero(endTimeObj.getDate())
                      + 'T' + addZero(endTimeObj.getHours()) + ":" + addZero(endTimeObj.getMinutes()) + ":" + addZero(endTimeObj.getSeconds())

        return $http.post('/getRentrakData/', {network: network, start_time: stringStart, end_time: stringEnd, metrics: metricsList})
        .then(function(res){
            return res.data;
        });
    }

    function addZero(i) {
        if (i < 10) {
            i = "0" + i;
        }
        return i;
    }

    return {
        getRentrakData: getRentrakData
    };
}]);