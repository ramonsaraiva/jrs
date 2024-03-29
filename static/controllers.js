'use strict';

var controllers = angular.module('controllers', []);

controllers.controller('nav_controller', function ($scope, $location, User)
{
    $scope.user = User;
    
    $scope.is_active = function (view_location) {
        var active = (view_location === $location.path());
        return active;
    };
    
    $scope.logout = function()
    {
        User.clear();
        $location.path('/login');
    }
});

controllers.controller('login_controller', function ($scope, $location, $http, User, Notify)
{
    $scope.error = false;
    
    $scope.login = function()
    {
        $scope.error = false;
        
        $http.post('/authentication', {'user': $scope.user, 'password': $scope.password})
            .success(function(data) {
                User.set_token(data.token);
                User.set(data.user);
                
                Notify.message('green', 'Bem vindo de volta, ' + User.get().name + '.');
                $location.path('/')
            })
            .error(function(error) {
                $scope.error = true;
            })
    }
});

controllers.controller('dashboard_controller', function($scope) 
{
});

controllers.controller('catalogue_controller', function($scope, ProductResource, Grid) {
    $scope.grid = Grid;
    $scope.filter = {}
    $scope.filter.query = '';
    $scope.filter.price = '';

    ProductResource.query(function(data) {
        $scope.catalogue = data.results;
    });
});

controllers.controller('customers_controller', function($scope, CustomerResource)
{
    $scope.customers = [];

    CustomerResource.query(function(data) {
        console.log(data.results);
        $scope.customers = data.results;
    });
});

controllers.controller('create_customer_controller', function($scope, $filter, $location,
            CityResource, CEPResource, CustomerResource, Notify)
{
    $scope.saving = false;
    $scope.customer = {};

    CityResource.query(function(data) {
        $scope.cities = data.results;
    });

    $scope.create_customer = function()
    {
        $scope.saving = true;

        var customer = new CustomerResource($scope.customer);
        customer.$save(function(data) {
            $scope.saving = false;
            Notify.create('Cliente', data.name);
            $location.path('/clientes');
        });
    }

    $scope.request_cep = function()
    {
        if (!$scope.customer.cep)
        {
            return;
        }

        CEPResource.get({id: $scope.customer.cep}, function(data) {
            var city = $filter('filter')($scope.cities, {name: data.city});

            if (city)
            {
                $scope.customer.city = city[0].id;
            }

            $scope.customer.address = data.address;
            $scope.customer.district = data.district;
        });
    }
});

controllers.controller('create_order_controller', function($scope, $filter, $location,
            User, CompanyResource, CustomerResource, OrderResource) {
    $scope.user = User;
    $scope.now = new Date();
    $scope.order = {};
    $scope.order.freight = 'CIF';

    $scope.companies = [];
    $scope.customers = [];

    CompanyResource.query(function(data) {
        $scope.companies = data.results;
        console.log(data.results);
    });

    CustomerResource.query(function(data) {
        $scope.customers = data.results;
        console.log(data.results);
    });

    $scope.open_order = function() 
    {
        var order = new OrderResource($scope.order);
        order.$save(function(data) {
            console.log(data);
        });
    }

});

controllers.controller('administration_controller', function($scope,
            UserResource, CompanyResource, CollectionResource, ProductResource,
            Notify, Upload, Grid)
{
    $scope.user = {};
    $scope.company = {};
    $scope.collection = {};
    $scope.product = {};
    $scope.grid = Grid;

    /* user crud */
    
    $scope.create_user = function()
    {
        var user = new UserResource($scope.user);
        user.$save(function(data) {
            $scope.users.push(user);
            Notify.create('Usuário', user.user);
            $scope.user = {};
        });
    }
    
    $scope.update_user = function(user)
    {
        var index = $scope.users.indexOf(user);

        UserResource.update({id: user.id}, user, function(data) {
            $scope.users[index].edit = false;
            Notify.update('Usuário', user.user);
        });
    }
    
    $scope.delete_user = function(user)
    {
        var index = $scope.users.indexOf(user);

        UserResource.delete({id: user.id}, function(data) {
            $scope.users.splice(index, 1);
            Notify.delete('Usuário', user.user);
        });
    }

    /* company crud */

    $scope.create_company = function()
    {
        var company = new CompanyResource($scope.company);
        company.$save(function(data) {
            $scope.companies.push(company);
            Notify.create('Empresa', company.name);
            $scope.company = {};
        });
    }

    $scope.update_company = function(company)
    {
        var index = $scope.companies.indexOf(company);
        CompanyResource.update({id: company.id}, company, function(data) {
            $scope.companies[index].edit = false;
            Notify.update('Empresa', company.name);
        });
    }

    $scope.delete_company = function(company)
    {
        var index = $scope.companies.indexOf(company);
        CompanyResource.delete({id: company.id}, function(data) {
            $scope.companies.splice(index, 1);
            Notify.delete('Empresa', company.name);
        });
    }

    /* collection crud */

    $scope.create_collection = function()
    {
        var collection = new CollectionResource($scope.collection);
        collection.$save(function(data) {
            $scope.collections.push(collection);
            Notify.create('Coleção', collection.name);
            $scope.collection = {};
        });
    }

    $scope.update_collection = function(collection)
    {
        var index = $scope.collections.indexOf(collection);
        CollectionResource.update({id: collection.id}, collection, function(data) {
            $scope.collections[index].edit = false;
            Notify.update('Coleção', collection.name);
        });
    }

    $scope.delete_collection = function(collection)
    {
        var index = $scope.collections.indexOf(collection);
        CollectionResource.delete({id: collection.id}, function(data) {
            $scope.collections.splice(index, 1);
            Notify.delete('Coleção', collection.name);
        });
    }
    

    /* product crud */

    $scope.create_product = function()
    {
        var product = new ProductResource($scope.product);
        product.$save(function(data) {
            $scope.products.push(product);
            Notify.create('Produto', product.code);
            $scope.product = {};
        });
    }

    $scope.update_product = function(product)
    {
        console.log(product);
        var index = $scope.products.indexOf(product);
        ProductResource.update({id: product.id}, product, function(data) {
            $scope.products[index].edit = false;
            $scope.products[index]._grid = Grid.parse(data.grid);
            Notify.update('Produto', product.code);
        });
    }

    $scope.delete_product = function(product)
    {
        var index = $scope.products.indexOf(product);
        ProductResource.delete({id: product.id}, function(data) {
            $scope.products.splice(index, 1);
            Notify.delete('Produto', product.name);
        });
    }

    $scope.upload_image = function(product, file, error_files)
    {
        if (file)
        {
            file.upload = Upload.upload({
                url: '/products/image',
                data: {file: file}
            });

            file.upload.then(function(response) {
                $scope.product.image = response.data.temp;
            });
        }
    }

    /* load */

    $scope.load_companies = function()
    {
        CompanyResource.query(function(data) {
            $scope.companies = data.results;
            $scope.displayed_companies = [].concat($scope.companies);
        });
    }

    $scope.load_collections = function()
    {
        $scope.load_companies();

        CollectionResource.query(function(data) {
            $scope.collections = data.results;
            $scope.displayed_collections = [].concat($scope.collections);
        });
    }

    $scope.load_products = function()
    {
        if ($scope.companies == null)
        {
            $scope.load_companies();
        }

        if ($scope.collections == null)
        {
            $scope.load_collections();
        }

        ProductResource.query(function(data) {
            $scope.products = data.results;
            $scope.displayed_products = [].concat($scope.products);
        });
    }

    /* start */

    UserResource.query(function (data) {
        $scope.users = data.results;
        $scope.displayed_users = [].concat($scope.users);
    })
});
