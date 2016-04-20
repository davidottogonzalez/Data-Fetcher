angular.module('myApp').directive('formattingData', function() {
    return {
        restrict: "E",
        scope: {
          unFormattedData: '=data',
          formatType: '=type'
        },
        link: function(scope, elt, attrs) {
            scope.$watch("unFormattedData",function(newValue,oldValue) {
                scope.formatData = '';

                switch(scope.formatType){
                    case 'number':
                        if(typeof scope.unFormattedData == 'undefined'){
                            scope.formatData = '';
                        }else{
                            scope.formatData = scope.unFormattedData.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                        }
                        break;
                    case 'percent':
                        scope.formatData = (parseFloat(scope.unFormattedData) * 100).toFixed(2) + "%"
                        break;
                    default:
                        scope.formatData = scope.unFormattedData;
                }
            });
        },
        templateUrl: 'static/directives/partials/formatting_directive.html'
    };
})