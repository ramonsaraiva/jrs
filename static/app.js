'use strict';

var app = angular.module('app', [
    'ngRoute',
    'ngResource',
    'LocalStorageModule',
    'ngSanitize',
    'ui.bootstrap',
    'angularMoment',
    'chart.js',
    'ui.select',
    'angularSpinner',
    'smart-table',
    'cgNotify',
    'colorpicker.module',
    'ngTagsInput',
    'controllers',
    'services',
    'directives',
    'filters'
]);

app.config(['$routeProvider', '$provide', '$httpProvider', function($routeProvider, $provide, $httpProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'partials/home.tpl.html',
            controller: 'home_controller'
        })
        .when('/login', {
            templateUrl: 'partials/login.tpl.html',
            controller: 'login_controller'
        })
        .when('/administracao', {
            templateUrl: 'partials/administration.tpl.html',
            controller: 'administration_controller'
        })
        .otherwise({
            redirectTo: '/'
        });
        
        $provide.factory('HttpInterceptor', function($q, $location, User, usSpinnerService) {
            return {
                request: function(config) {
                    
                    usSpinnerService.spin('spinner');
                    
                    var token = User.get_token();
    
                    if (token)
                    {
                        config.headers['Authorization'] = 'bearer ' + token;
                    }
    
                    return config || $q.when(config);
                },
    
                responseError: function(rejection) {
                    
                    usSpinnerService.stop('spinner');
                    
                    if (rejection.status == 401)
                    {
                        User.clear();
                        $location.path('/login');
                    }
    
                    return $q.reject(rejection);
                },
                
                response: function(response)
                {
                    usSpinnerService.stop('spinner');
                    
                    return response;
                }
            }
        });

        $httpProvider.interceptors.push('HttpInterceptor');
}]);

app.run(function($rootScope, $location, User, usSpinnerService)
{
    $rootScope.$on('$routeChangeStart', function(event, next, current)
    {
        if (!User.logged())
        {
            if (next.templateuRL != 'partials/login.tpl.html')
            {
                $location.path('/login');
            }
        }
    });
})
