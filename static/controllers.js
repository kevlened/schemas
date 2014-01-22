var schemaApp = angular.module('schemaApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('{[').endSymbol(']}');
    }
);
 
schemaApp.controller('SchemaListCtrl', function ($scope, $http) {

	$http.get('schemas').success(function(data) {
		$scope.dbs = data;
	});
	  
	$scope.addDatabase = function() {
		$http.post('add_schema', $scope.new).success(function(success) {
			if(success === true){
				$scope.dbs.push({'name':$scope.new.name});
			}
			else{
				alert('Could not add the database');
			}
			//$scope.$apply();
			//return true;
		});
	}
	
	$scope.engines = ['sqlite','oracle','mysql','postgres','mssql'];
	
	$scope.new = {};
	$scope.new.engine = '';
	$scope.new.name = '';
	$scope.new.username = '';
	$scope.new.password = '';
	$scope.new.host = '';
});