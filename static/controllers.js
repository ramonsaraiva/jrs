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

controllers.controller('home_controller', function($scope, $location, $filter) 
{
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
