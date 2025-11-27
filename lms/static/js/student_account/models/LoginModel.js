(function(define) {
    'use strict';

    define([
        'jquery',
        'backbone',
        'jquery.url'
    ], function($, Backbone) {
        console.log('[LoginModel] LoginModel module loaded');
        return Backbone.Model.extend({
            defaults: {
                email: '',
                password: ''
            },

            ajaxType: '',
            urlRoot: '',

            initialize: function(attributes, options) {
                console.log('[LoginModel] LoginModel initializing with attributes:', attributes, 'options:', options);
                this.ajaxType = options.method;
                this.urlRoot = options.url;
                console.log('[LoginModel] LoginModel initialized - ajaxType:', this.ajaxType, 'urlRoot:', this.urlRoot);
            },

            sync: function(method, model) {
                var headers = {'X-CSRFToken': $.cookie('csrftoken')},
                    data = {},
                    analytics,
                    courseId = $.url('?course_id');

                // If there is a course ID in the query string param,
                // send that to the server as well so it can be included
                // in analytics events.
                if (courseId) {
                    analytics = JSON.stringify({
                        enroll_course_id: decodeURIComponent(courseId)
                    });
                }

                // Include all form fields and analytics info in the data sent to the server
                $.extend(data, model.attributes, {analytics: analytics});

                console.log('[LoginModel] Starting AJAX request to:', model.urlRoot);
                console.log('[LoginModel] Request data:', data);
                console.log('[LoginModel] Request headers:', headers);
                
                $.ajax({
                    url: model.urlRoot,
                    type: model.ajaxType,
                    data: data,
                    headers: headers,
                    success: function(response, textStatus, xhr) {
                        console.log('[LoginModel] AJAX Success!');
                        console.log('[LoginModel] Response:', response);
                        console.log('[LoginModel] Text Status:', textStatus);
                        console.log('[LoginModel] XHR Status:', xhr.status);
                        console.log('[LoginModel] Response type:', typeof response);
                        
                        // Store the response data in the model for the view to access
                        model.set('response', response);
                        console.log('[LoginModel] Triggering sync event with response');
                        model.trigger('sync', model, response);
                    },
                    error: function(xhr, status, error) {
                        console.error('[LoginModel] AJAX Error!');
                        console.error('[LoginModel] Status:', status);
                        console.error('[LoginModel] Error:', error);
                        console.error('[LoginModel] XHR Response:', xhr.responseText);
                        console.error('[LoginModel] XHR Status:', xhr.status);
                        model.trigger('error', xhr);
                    }
                });
            }
        });
    });
}).call(this, define || RequireJS.define);
