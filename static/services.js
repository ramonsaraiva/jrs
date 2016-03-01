'use strict';

var services = angular.module('services', []);

services.factory('User', function(localStorageService) {
	return {
		set: function(data) {
			localStorageService.set('user', data);
		},

		get: function() {
			return localStorageService.get('user');
		},

		set_token: function(token)
		{
			localStorageService.set('token', token);
		},

		get_token: function()
		{
			return localStorageService.get('token');
		},

		logged: function() {
			return localStorageService.get('user') != null;
		},

		clear: function() {
			this.set(null);
			this.set_token(null);
		}
	}
});

services.factory('Notify', function(notify) {
	var _classes = {
		green: 'alert-success',
		yellow: 'alert-warning',
		red: 'alert-danger'
	}
	
	var push = function(type, msg)
	{
		notify({
			message: msg,
			classes: _classes[type],
			position: 'center',
			duration: 2000
		});
	}
	
	return {
		message: function(type, msg) {
			push(type, msg);
		},
		
		create: function(obj, ident)
		{
			push('green', obj + ' ' + ident + ' foi criado(a) com sucesso');
		},
		
		update: function(obj, ident)
		{
			push('green', obj + ' ' + ident + ' foi atualizado(a) com sucesso');
		},
		
		delete: function(obj, ident)
		{
			push('yellow', obj + ' ' + ident + ' foi deletado(a) com sucesso');
		}
	}
});

services.factory('Grid', function() {
    return {
        parse: function(data) {
            if (data == null)
            {
                return null;
            }

            var grid = {};

            var lines = data.split('\n');
            grid.colors = lines[0].split(',');
            grid.sizes = [];

            for (var i = 1; i < lines.length; i++)
            {
                grid.sizes.push(lines[i].split(','));
            }

            return grid;
        }
    }
});

services.factory('UserResource', function($resource) {
	return $resource('/users/:id', {id: '@id'}, {
		query: {
			method: 'get',
			isarray: false
		},
		update: {
			method: 'put'
		}
	});
});

services.factory('CompanyResource', function($resource) {
	return $resource('/companies/:id', {id: '@id'}, {
		query: {
			method: 'get',
			isarray: false
		},
		update: {
			method: 'put'
		}
	});
});

services.factory('CollectionResource', function($resource) {
	return $resource('/collections/:id', {id: '@id'}, {
		query: {
			method: 'get',
			isarray: false
		},
		update: {
			method: 'put'
		}
	});
});

services.factory('ProductResource', function($resource) {
	return $resource('/products/:id', {id: '@id'}, {
		query: {
			method: 'get',
			isarray: false
		},
		update: {
			method: 'put'
		}
	});
});
