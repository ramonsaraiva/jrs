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
    'ngFileUpload',
    'controllers',
    'services',
    'directives',
    'filters'
]);

app.config(['$routeProvider', '$provide', '$httpProvider', function($routeProvider, $provide, $httpProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'partials/dashboard.tpl.html',
            controller: 'dashboard_controller'
        })
        .when('/login', {
            templateUrl: 'partials/login.tpl.html',
            controller: 'login_controller'
        })
        .when('/catalogo', {
            templateUrl: 'partials/catalogue.tpl.html',
            controller: 'catalogue_controller'
        })
        .when('/clientes', {
            templateUrl: 'partials/customers.tpl.html',
            controller: 'customers_controller'
        })
        .when('/clientes/criar', {
            templateUrl: 'partials/create_customer.tpl.html',
            controller: 'create_customer_controller'
        })
        .when('/pedidos', {
            templateurl: 'partials/orders.tpl.html',
            controller: 'orders_controller'
        })
        .when('/pedidos/criar', {
            templateUrl: 'partials/create_order.tpl.html',
            controller: 'create_order_controller'
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
