var schemaApp = angular.module('schemaApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('{[').endSymbol(']}');
    }
);
 
schemaApp.controller('SchemaListCtrl', function ($scope, $http) {

	$http.get('schemas').success(function(data) {
		$scope.dbs = data;
	});
	  
	$scope.addDatabase = function() {
		$http.post('add_schema', $scope.new).success(function(data) {
			$scope.dbs.push({'name':$scope.new.name});
			$scope.$apply();
			return true;
		});
	}
	
	$scope.new = {};
	$scope.new.engine = '';
	$scope.new.name = '';
	$scope.new.username = '';
	$scope.new.password = '';
	$scope.new.host = '';
});