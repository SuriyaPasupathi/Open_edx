(function(define) {
    'use strict';

    console.log('[LogistrationFactory] LogistrationFactory module loading...');

    define([
        'jquery',
        'js/student_account/views/AccessView'
    ],
    function($, AccessView) {
        console.log('[LogistrationFactory] LogistrationFactory module loaded, dependencies resolved');
        return function(options) {
            console.log('[LogistrationFactory] LogistrationFactory called with options:', options);
            var $logistrationElement = $('#login-and-registration-container');
            console.log('[LogistrationFactory] Found logistration element:', $logistrationElement.length > 0 ? 'YES' : 'NO');
            console.log('[LogistrationFactory] Element:', $logistrationElement);

            // eslint-disable-next-line no-new
            console.log('[LogistrationFactory] Creating AccessView instance...');
            new AccessView(_.extend(options, {el: $logistrationElement}));
            console.log('[LogistrationFactory] AccessView instance created');
        };
    }
    );
}).call(this, define || RequireJS.define);
