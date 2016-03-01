'use strict';

var directives = angular.module('directives', []);

directives.directive('selectpicker', function() {
  return {
    restrict: 'E',
    scope: {
      array: '=',
      model: '=',
      class: '='
    },
    template: '<select class="selectpicker" ng-model="model" ng-options="o.value as o.option for o in array"></select>',
    replace: true,
    link: function(scope, element, attrs) {
      $(element).selectpicker();
    }
  }
});

/* mallocced from stackoverflow */

directives.directive('ngReallyClick', ['$uibModal',
    function($uibModal) {

      var ModalInstanceCtrl = function($scope, $uibModalInstance) {
        $scope.ok = function() {
          $uibModalInstance.close();
        };

        $scope.cancel = function() {
          $uibModalInstance.dismiss('cancel');
        };
      };

      return {
        restrict: 'A',
        scope: {
          ngReallyClick: "&",
          item: "="
        },
        link: function(scope, element, attrs) {
          element.bind('click', function() {
            var message = attrs.ngReallyMessage || "Are you sure ?";

            /*
            //This works
            if (message && confirm(message)) {
              scope.$apply(attrs.ngReallyClick);
            }
            //*/

            //*This doesn't works
            var modalHtml = '<div class="modal-body">' + message + '</div>';
            modalHtml += '<div class="modal-footer"><button class="btn btn-primary" ng-click="ok()">OK</button><button class="btn btn-default" ng-click="cancel()">Cancelar</button></div>';

            var modalInstance = $uibModal.open({
              template: modalHtml,
              controller: ModalInstanceCtrl
            });

            modalInstance.result.then(function() {
              scope.ngReallyClick({
                item: scope.item
              }); //raise an error : $digest already in progress
            }, function() {
              //Modal dismissed
            });
            //*/

          });

        }
      }
    }
  ]);
