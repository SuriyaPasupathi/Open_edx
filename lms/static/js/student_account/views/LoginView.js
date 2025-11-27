(function(define) {
    'use strict';

    define([
        'jquery',
        'underscore',
        'gettext',
        'edx-ui-toolkit/js/utils/html-utils',
        'edx-ui-toolkit/js/utils/string-utils',
        'js/student_account/views/FormView',
        'text!templates/student_account/form_success.underscore',
        'text!templates/student_account/form_status.underscore'
    ], function(
        $, _, gettext,
        HtmlUtils,
        StringUtils,
        FormView,
        formSuccessTpl,
        formStatusTpl
    ) {
        console.log('[LoginView] LoginView module loaded');
        return FormView.extend({
            el: '#login-form',
            tpl: '#login-tpl',
            events: {
                'click .js-login': 'submitForm',
                'click .forgot-password': 'forgotPassword',
                'click .login-provider': 'thirdPartyAuth',
                'click .enterprise-login': 'enterpriseSlugLogin',
                'click .login-help': 'toggleLoginHelp',
                'submit form': 'submitForm'
            },
            
            initialize: function() {
                console.log('[LoginView] LoginView initialized');
                console.log('[LoginView] Element selector:', this.el);
                console.log('[LoginView] Events:', this.events);
                FormView.prototype.initialize.apply(this, arguments);
                
                // Debug: Check if the form element exists
                var $form = $(this.el);
                console.log('[LoginView] Form element found:', $form.length > 0);
                console.log('[LoginView] Form element:', $form);
                
                // Debug: Check if the submit button exists
                var $submitButton = $form.find('.js-login');
                console.log('[LoginView] Submit button found:', $submitButton.length > 0);
                console.log('[LoginView] Submit button:', $submitButton);
                
                // Debug: Manually bind click event to test
                $submitButton.on('click', function(e) {
                    console.log('[LoginView] Submit button clicked manually!');
                    e.preventDefault();
                });
            },
            formType: 'login',
            requiredStr: '',
            optionalStr: '',
            submitButton: '.js-login',
            formSuccessTpl: formSuccessTpl,
            formStatusTpl: formStatusTpl,
            authWarningJsHook: 'js-auth-warning',
            passwordResetSuccessJsHook: 'js-password-reset-success',
            defaultFormErrorsTitle: gettext('We couldn\'t sign you in.'),
            isEnterpriseEnable: false,

            preRender: function(data) {
                this.providers = data.thirdPartyAuth.providers || [];
                this.hasSecondaryProviders = (
                    data.thirdPartyAuth.secondaryProviders && data.thirdPartyAuth.secondaryProviders.length
                );
                this.currentProvider = data.thirdPartyAuth.currentProvider || '';
                this.syncLearnerProfileData = data.thirdPartyAuth.syncLearnerProfileData || false;
                this.errorMessage = data.thirdPartyAuth.errorMessage || '';
                this.platformName = data.platformName;
                this.resetModel = data.resetModel;
                this.accountRecoveryModel = data.accountRecoveryModel;
                this.supportURL = data.supportURL;
                this.passwordResetSupportUrl = data.passwordResetSupportUrl;
                this.createAccountOption = data.createAccountOption;
                this.showRegisterLinks = (
                    typeof data.showRegisterLinks !== 'undefined'
                ) ? data.showRegisterLinks : this.showRegisterLinks;
                this.accountActivationMessages = data.accountActivationMessages;
                this.accountRecoveryMessages = data.accountRecoveryMessages;
                this.hideAuthWarnings = data.hideAuthWarnings;
                this.pipelineUserDetails = data.pipelineUserDetails;
                this.enterpriseName = data.enterpriseName;
                this.enterpriseSlugLoginURL = data.enterpriseSlugLoginURL;
                this.isEnterpriseEnable = data.isEnterpriseEnable;
                this.is_require_third_party_auth_enabled = data.is_require_third_party_auth_enabled || false;

                console.log('[LoginView.preRender] Setting up event listeners');
                this.listenTo(this.model, 'sync', this.saveSuccess);
                this.listenTo(this.resetModel, 'sync', this.resetEmail);
                this.listenTo(this.accountRecoveryModel, 'sync', this.resetEmail);
                console.log('[LoginView.preRender] Event listeners set up - model sync will call saveSuccess');
            },

            render: function(html) {
                var fields = html || '';

                HtmlUtils.setHtml(
                    $(this.el),
                    HtmlUtils.HTML(
                        _.template(this.tpl)({
                            // We pass the context object to the template so that
                            // we can perform variable interpolation using sprintf
                            HtmlUtils: HtmlUtils,
                            context: {
                                fields: fields,
                                currentProvider: this.currentProvider,
                                syncLearnerProfileData: this.syncLearnerProfileData,
                                providers: this.providers,
                                hasSecondaryProviders: this.hasSecondaryProviders,
                                platformName: this.platformName,
                                createAccountOption: this.createAccountOption,
                                pipelineUserDetails: this.pipelineUserDetails,
                                enterpriseName: this.enterpriseName,
                                is_require_third_party_auth_enabled: this.is_require_third_party_auth_enabled
                            }
                        })
                    )
                );
                this.postRender();

                return this;
            },

            postRender: function() {
                var formErrorsTitle;
                this.$container = $(this.el);
                this.$form = this.$container.find('form');
                this.$formFeedback = this.$container.find('.js-form-feedback');
                this.$submitButton = this.$container.find(this.submitButton);

                if (this.errorMessage) {
                    formErrorsTitle = _.sprintf(
                        gettext('An error occurred when signing you in to %s.'),
                        this.platformName
                    );
                    this.renderErrors(formErrorsTitle, [this.errorMessage]);
                } else if (this.currentProvider) {
                    /* If we're already authenticated with a third-party
                     * provider, try logging in. The easiest way to do this
                     * is to simply submit the form.
                     */
                    this.model.save();
                }

                // Display account activation success or error messages.
                this.renderAccountActivationMessages();
                this.renderAccountRecoveryMessages();
            },

            renderAccountActivationMessages: function() {
                _.each(this.accountActivationMessages, this.renderMessage, this);
            },

            renderAccountRecoveryMessages: function() {
                _.each(this.accountRecoveryMessages, this.renderMessage, this);
            },

            renderMessage: function(message) {
                this.renderFormFeedback(this.formStatusTpl, {
                    jsHook: message.tags,
                    message: HtmlUtils.HTML(message.message)
                });
            },

            forgotPassword: function(event) {
                event.preventDefault();

                this.trigger('password-help');
                this.clearPasswordResetSuccess();
            },

            toggleLoginHelp: function(event) {
                var $help;
                event.preventDefault();
                $help = $('#login-help');
                this.toggleHelp(event, $help);
            },

            enterpriseSlugLogin: function(event) {
                event.preventDefault();
                if (this.enterpriseSlugLoginURL) {
                    window.location.href = this.enterpriseSlugLoginURL;
                }
            },

            postFormSubmission: function() {
                this.clearPasswordResetSuccess();
            },

            resetEmail: function() {
                var email = $('#password-reset-email').val(),
                    successTitle = gettext('Check Your Email'),
                    successMessageHtml = HtmlUtils.interpolateHtml(
                        gettext('{paragraphStart}You entered {boldStart}{email}{boldEnd}. If this email address is associated with your {platform_name} account, we will send a message with password recovery instructions to this email address.{paragraphEnd}' // eslint-disable-line max-len
                        + '{paragraphStart}If you do not receive a password reset message after 1 minute, verify that you entered the correct email address, or check your spam folder.{paragraphEnd}' // eslint-disable-line max-len
                        + '{paragraphStart}If you need further assistance, {anchorStart}contact technical support{anchorEnd}.{paragraphEnd}'), { // eslint-disable-line max-len
                            boldStart: HtmlUtils.HTML('<b data-hj-suppress>'),
                            boldEnd: HtmlUtils.HTML('</b>'),
                            paragraphStart: HtmlUtils.HTML('<p>'),
                            paragraphEnd: HtmlUtils.HTML('</p>'),
                            email: email,
                            platform_name: this.platformName,
                            anchorStart: HtmlUtils.HTML(
                                StringUtils.interpolate(
                                    '<a href="{passwordResetSupportUrl}">', {
                                        passwordResetSupportUrl: this.passwordResetSupportUrl
                                    }
                                )
                            ),
                            anchorEnd: HtmlUtils.HTML('</a>')
                        }
                    );

                this.clearFormErrors();
                this.clearPasswordResetSuccess();

                this.renderFormFeedback(this.formSuccessTpl, {
                    jsHook: this.passwordResetSuccessJsHook,
                    title: successTitle,
                    messageHtml: successMessageHtml
                });
            },

            thirdPartyAuth: function(event) {
                var providerUrl = $(event.currentTarget).data('provider-url') || '';

                if (providerUrl) {
                    window.location.href = providerUrl;
                }
            },

            saveSuccess: function(model, response) {
                console.log('[LoginView.saveSuccess] ===== LOGIN SUCCESS CALLBACK START =====');
                console.log('[LoginView.saveSuccess] model:', model);
                console.log('[LoginView.saveSuccess] response:', response);
                console.log('[LoginView.saveSuccess] model attributes:', model && model.attributes);
                console.log('[LoginView.saveSuccess] model response data:', model && model.get && model.get('response'));
                
                var redirectUrl = null;

                // response may be JSON with redirect_url when using Backbone.sync
                if (response && response.redirect_url) {
                    redirectUrl = response.redirect_url;
                    console.log('[LoginView.saveSuccess] Found redirect_url in response:', redirectUrl);
                }

                // as a fallback, check model attributes
                if (!redirectUrl && model && typeof model.get === 'function') {
                    redirectUrl = model.get('redirect_url');
                    console.log('[LoginView.saveSuccess] Found redirect_url in model attributes:', redirectUrl);
                }
                
                // Check model response data
                if (!redirectUrl && model && model.get && model.get('response')) {
                    var modelResponse = model.get('response');
                    if (modelResponse && modelResponse.redirect_url) {
                        redirectUrl = modelResponse.redirect_url;
                        console.log('[LoginView.saveSuccess] Found redirect_url in model response data:', redirectUrl);
                    }
                }

                console.log('[LoginView.saveSuccess] Final chosen redirectUrl:', redirectUrl);

                if (redirectUrl) {
                    console.log('[LoginView.saveSuccess] REDIRECTING TO:', redirectUrl);
                    console.log('[LoginView.saveSuccess] Setting window.location.href...');
                    window.location.href = redirectUrl;
                    console.log('[LoginView.saveSuccess] Redirect command executed');
                } else {
                    console.warn('[LoginView.saveSuccess] NO REDIRECT URL FOUND!');
                    console.warn('[LoginView.saveSuccess] Response object keys:', response ? Object.keys(response) : 'null');
                    console.warn('[LoginView.saveSuccess] Model keys:', model ? Object.keys(model.attributes || {}) : 'null');
                    console.warn('[LoginView.saveSuccess] Triggering auth-complete event as fallback');
                    this.trigger('auth-complete');
                }

                this.clearPasswordResetSuccess();
                console.log('[LoginView.saveSuccess] ===== LOGIN SUCCESS CALLBACK END =====');
            },

            saveError: function(error) {
                var errorCode;
                var msg;
                if (error.status === 0) {
                    msg = gettext('An error has occurred. Check your Internet connection and try again.');
                } else if (error.status === 500) {
                    msg = gettext('An error has occurred. Try refreshing the page, or check your Internet connection.'); // eslint-disable-line max-len
                } else if (error.responseJSON !== undefined && error.responseJSON.error_code === 'inactive-user') {
                    msg = HtmlUtils.interpolateHtml(
                        gettext('In order to sign in, you need to activate your account.{line_break}{line_break}'
                            + 'We just sent an activation link to {strong_start} {email} {strong_end}. If '
                            + ' you do not receive an email, check your spam folders or '
                            + ' {anchorStart}contact {platform_name} Support{anchorEnd}.'),
                        {
                            email: error.responseJSON.email,
                            platform_name: this.platform_name,
                            line_break: HtmlUtils.HTML('<br/>'),
                            strong_start: HtmlUtils.HTML('<strong>'),
                            strong_end: HtmlUtils.HTML('</strong>'),
                            anchorStart: HtmlUtils.HTML(
                                StringUtils.interpolate(
                                    '<a href="{SupportUrl}">', {
                                        SupportUrl: this.supportURL,
                                    }
                                )
                            ),
                            anchorEnd: HtmlUtils.HTML('</a>')
                        }
                    );
                } else if (error.responseJSON !== undefined) {
                    msg = error.responseJSON.value;
                    errorCode = error.responseJSON.error_code;
                } else {
                    msg = gettext('An unexpected error has occurred.');
                }

                this.errors = [
                    StringUtils.interpolate(
                        '<li>{msg}</li>', {
                            msg: msg
                        }
                    )
                ];
                this.clearPasswordResetSuccess();

                /* If the user successfully authenticated with a third-party provider, but they haven't
                 * linked the accounts, instruct the user on how to link the accounts.
                 */
                if (errorCode === 'third-party-auth-with-no-linked-account' && this.currentProvider) {
                    if (!this.hideAuthWarnings) {
                        this.clearFormErrors();
                        this.renderThirdPartyAuthWarning();
                    }
                } else {
                    this.renderErrors(this.defaultFormErrorsTitle, this.errors);
                }
                this.toggleDisableButton(false);
            },

            renderThirdPartyAuthWarning: function() {
                var message = _.sprintf(
                    gettext('You have successfully signed into %(currentProvider)s, but your %(currentProvider)s'
                            + ' account does not have a linked %(platformName)s account. To link your accounts,'
                            + ' sign in now using your %(platformName)s password.'),
                    {currentProvider: this.currentProvider, platformName: this.platformName}
                );

                this.clearAuthWarning();
                this.renderFormFeedback(this.formStatusTpl, {
                    jsHook: this.authWarningJsHook,
                    message: message
                });
            },

            clearPasswordResetSuccess: function() {
                var query = '.' + this.passwordResetSuccessJsHook;
                this.clearFormFeedbackItems(query);
            },

            clearAuthWarning: function() {
                var query = '.' + this.authWarningJsHook;
                this.clearFormFeedbackItems(query);
            }
        });
    });
}).call(this, define || RequireJS.define);
