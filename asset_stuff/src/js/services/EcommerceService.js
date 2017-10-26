BH.add('EcommerceService', function() {
	
	"use strict";
    eval(BH.System);

    var EcommerceService = BH.Class(BH.Widget, {

		// REF: https://github.com/allumestyle/ecommerce-service/blob/master/includes/api/allume/online/class-allume-rest-orders-controller.php`
		// REF: https://github.com/allumestyle/ecommerce-service/blob/master/includes/api/allume/online/class-allume-rest-user-controller.php (get_register_schema)

	    register: function(data, successCb, errorCb) {
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/users/register', data, successCb, errorCb);
	    },		
		
		// Used by Free/Paid.js when processing BH.EcommerceService.createLogin
        processError: function(data) {
	        var error = BH.Constants.DEFAULT_ERROR_MESSAGE;
	        
	        if (typeof(data.error) === 'string') {
		        
				if (data.error === 'password_validation_failed') {
					error = 'Unacceptable password';

                } else if (data.error.indexOf('username_exists') > -1) {
                    error = 'Email already in use';
                             
				} else if (data.error === 'email_exists') {
                    error = 'Email already in use';

				} else if (data.error === 'empty_first_name') {
                    error = 'Empty first name';

				} else if (data.error === 'phone_exists') {
                    error = 'Phone already in use';
				}
	        }
	        
	        return error;
        },		

	    forgotPassword: function(data, successCb, errorCb) {
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/users/lostPassword', data, successCb, errorCb);
	    },

        isDueStylingFeeRefund: function(data, successCb, errorCb) {
            this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/orders/is_styling_fee_refund_due', data, successCb, errorCb);
        },

		isLoggedIn: function(successCb, errorCb) {
			this._ajax('GET', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/users/is_logged_in', {}, successCb, errorCb);
		},
	    
	    isValidReferralCodeWillFullDiscount: function(data, successCb, errorCb) {
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/orders/is_valid_referral_code_will_full_discount', data, successCb, errorCb);
	    },
	    
	    login: function(data, successCb, errorCb) {
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/users/login', data, successCb, errorCb);
	    },

	    logout: function(successCb, errorCb) {
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/users/logout', {}, successCb, errorCb);
	    },

	    resetPassword: function(data, successCb, errorCb) {
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/users/resetPassword', data, successCb, errorCb);
	    },

	    //
	    
		addToCart: function(config, successCb, errorCb) {
			var useThisImage = '';
			
			if ((config.color_images) && (typeof(config.color_images) != 'undefined')) {
				// Use currently selected color image
				var foundImages = $.grep(config.color_images, function(e) { return e.image_size == 'xl'; });
				useThisImage = foundImages[0].image_url;
			}
			
			if ((useThisImage === '') && (config.product_data.product_image)) {
				useThisImage = config.product_data.product_image;
			}
			
			var data = {
				product_id: config.product_data.product_id,
				quantity: config.qty,
				user_viewed_main_image_url: useThisImage,
				variation_info: config.variant,
				look_token: config.product_data.look_token
			};

			if (config.edited_product) {
				data.edited_product = config.edited_product;
			}	

			if ((config.hidden_variations) && (config.hidden_variations.join().length > 0)) {
				data.hidden_variations = config.hidden_variations.join();
			}
				
			BH.EcommerceService.addOrUpdateCartItem(
                data,
                function(data) {

                    if (successCb) {
                        successCb(data);
                    }

                }, function(error) {

                    if (errorCb) {
                        errorCb(error);
                    }

                    BH.log('ERROR (addToCart)', error);
                }
            );
		},

		addOrUpdateCartItem: function(data, successCb, errorCb) {
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/orders/addOrUpdateCartItem', data, successCb, errorCb);
		},
		
		addOrUpdateCartShippingAddress: function(data, successCb, errorCb) {
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/orders/addOrUpdateCartShippingAddress', data, successCb, errorCb);
		},
		
		addOrUpdateCartCreditCard: function(data, successCb, errorCb) {
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/orders/addOrUpdateCartCreditCard', data, successCb, errorCb);
		},
		
		getCart: function(successCb, errorCb) {
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/orders/loadCart', {}, successCb, errorCb);
		},
		
		getUserCreditCard: function(successCb, errorCb) {
			this._ajax('GET', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/orders/getUserCreditCard', {}, successCb, errorCb);
		},
		
		getUserShippingAddress: function(successCb, errorCb) {
			this._ajax('GET', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/orders/getUserShippingAddress', {}, successCb, errorCb);
		},

		purchase: function(data, successCb, errorCb) {
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/orders/purchase', data, successCb, errorCb);
		},
		
		purchaseStylingFee: function(data, successCb, errorCb) {
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/orders/purchase_styling_fee', data, successCb, errorCb);
		},
		
		// Save user's credit card for later use
		saveUserCreditCard: function (data, successCb, errorCb) {
			// https://github.com/allumestyle/ecommerce-service/blob/v2/includes/api/allume/online/class-allume-rest-orders-controller.php (get_add_credit_card_schema)
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/orders/setUserCreditCard', data, successCb, errorCb);
		},
		
	    // Writes visitorId to response header; necessary for EcommerceService.*
	    setVisitorId: function(successCb) {
		    // https://github.com/allumestyle/ecommerce-service/blob/v1/includes/api/allume/online/class-allume-rest-user-controller.php
			this._ajax('POST', BH.properties.ecommerceServiceAjaxHost + BH.properties.ajaxBase + '/users/setVisitorId', {}, function() {
				
				BH.GlobalEvents.get('setVisitorIdEvent').fire();
				
				// Use this in LooksHeader getCart; if works after a while then expand user to other APIs
				BH.Globals.haveVisitorId = true;
				
				if (successCb) {
					successCb();
				}
				
			}, null);
	    },
		
		_ajax: function(methodType, serviceUrl, serviceData, successCb, errorCb) {
			
			// Leaving this in but the initial case does not work. Revisit later.			
			var nonce = Cookies.get('allume-nonce');
			if (nonce !== 'null') {
				serviceData._wpnonce = nonce;
			}

			$.ajax({
				
				// You must use dev.allume.co instead of localhost or this does not work.
				crossDomain: true,
				xhrFields: {
					withCredentials: true
				},
				
				contentType: 'application/x-www-form-urlencoded',
				data: jQuery.param(serviceData) || jQuery.param({}),
				dataType: 'json',
				type: methodType,
			    url: serviceUrl
			}).done(function(response, status, xhr) {

				Cookies.set('allume-nonce', xhr.getResponseHeader('X-WP-Nonce'), { domain: '.allume.co', expires: 30, path: '/', secure: true });
			
				if (response.status === 'success') {
					if (successCb) {
						successCb(response.data);
					}
				} else {
					if (errorCb) {
						errorCb(response);
					} else {
						BH.log('ERROR', response);
					}
				}
			
			}).fail(function(error) {
				if (errorCb) {
					errorCb(error);
				} else {
					BH.log('FAIL (EcommerceService)', serviceUrl, error);
				}
			});
		}
		
    });

    if (!BH.EcommerceService) {
        BH.EcommerceService = new EcommerceService();
        BH.EcommerceService.render();
        
        BH.EcommerceService.setVisitorId();
        
        Bugsnag.notifyReleaseStages = ["production"]; // Only notify of production errors
    }
});