GLClient.controller('WBFileUploadCtrl', ['$scope', function($scope) {
  $scope.disabled = false;

  $scope.$on('flow::fileAdded', function (event, flow, file) {
    $scope.error_msg = undefined;
    if (file.size > $scope.node.maximum_filesize * 1024 * 1024) {
      $scope.error_msg = "This file exceeds the maximum upload size for this server.";
      event.preventDefault();
    } else {
      if ($scope.field !== undefined && !$scope.field.multi_entry) {
        // if the field allows to load only one file disable the button
        // as soon as a file is loaded.
        $scope.disabled = true;
      }
    }
  });
}]).
controller('ImageUploadCtrl', ['$scope', '$http', 'Authentication', function($scope, $http, Authentication) {
  $scope.get_auth_headers = Authentication.get_auth_headers;
  $scope.imageUploadObj = {};

  $scope.deletePicture = function() {
    $http({
      method: 'DELETE',
      url: $scope.imageUploadUrl,
      headers: $scope.get_auth_headers()
    }).then(function successCallback() {
      $scope.imageUploadModel[$scope.imageUploadModelAttr] = '';
      $scope.imageUploadObj.flow.files = [];
    }, function errorCallback() { });
  };
}]);
