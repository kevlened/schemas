var schemaApp = angular.module('schemaApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('{[').endSymbol(']}');
    }
);
 
schemaApp.controller('SchemaListCtrl', function ($scope) {
  $scope.dbs = [
  		{name:"Chinook_Sqlite.sqlite"}
  ];
});