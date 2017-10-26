BH.add('Util', function() {
	
	"use strict";
    eval(BH.System);

    var Util = BH.Class(BH.Widget, {

	    cleanPhone: function(phone) {
			return phone.replace(/[^\d]+/g, ''); // Remove everything except digits
	    },
	    
        // Given a JSON object (obj), remove all properties in the given array of property names (propertiesToKeep)
        filterObject: function(obj, propertiesToKeep) {
	        var newObject = {};
	        
			for (var property in obj) {
				for (var i = 0; i < propertiesToKeep.length; i++) {
					var toKeep = propertiesToKeep[i];
					if (obj.hasOwnProperty(toKeep)) {
						newObject[toKeep] = obj[toKeep];
					}
				}
			}
			
			return newObject;
        },

		getErrorMessage: function(error) {
			var msg = BH.Constants.DEFAULT_ERROR_MESSAGE;

            var _error = (error.status) ? error.status : error;
            if ($.type(_error) !== 'string') {
                _error = 'ERROR';
            }

			if (_error === 'existing_user_login') {
				msg = 'Oops, it looks like you already have an existing account.<br />To start a new session, <span class="peach">text your personal shopper at<br />650-278-4732</span>';

			} else if (_error === 'phone_exists') {
				msg = 'The cell phone provided has been used with another email address. Please try the email address you previously used.<br />If you still have a problem, please contact us at <a href="mailto:support@allume.co">support@allume.co</a> and we can update your account.';
			
			} else if (_error === 'invalid_email') {
				msg = 'That email is invalid';
			
			} else if (_error === 'invalidcombo') {
				msg = 'That phone is invalid';

			} else if (_error === 'old_quiz_version') {
				msg = 'Oops, while you were away we made a few updates to our style quiz. Please refresh your browser to continue with the updated version.';

			} else if (_error === 'cannot_book') {
				msg = 'Oops, the time-slot you chose is no longer available. Please refresh your browser and choose a time that works for you from the available time-slots.';

			} else if (_error === 'no_slots') {
				msg = 'All of the consultation times are currently taken. We\'re working to add more times to the schedule. You can text us at <span class="hidden-xs">650-278-4732</span><span class="visible-xs-inline-block"><a href="sms:6502784732">650-278-4732</a></span> and we\'ll be happy to help you.';

			} else if (_error === 'user_already_booked') {
				msg = 'Oops, it looks like you\'ve already scheduled a time for your consultation. If you need to reschedule please text us at <span class="hidden-xs">650-278-4732</span><span class="visible-xs-inline-block"><a href="sms:6502784732">650-278-4732</a></span> and we\'ll be happy to help you.';

			} else if (_error === 'color_size_not_available') {
				msg = 'That color/size is unavailable';

			} else if (_error === 'password_validation_failed') {
				msg = 'Unacceptable password';

			} else if (_error === 'email_exists') {
				msg = 'That email is already in use.';

			} else if (_error === 'invalid_username') {
				msg = 'Invalid phone/email';

			} else if (_error === 'incorrect_password') {
				msg = 'Incorrect password';

			} else if (_error === 'empty_username') {
				msg = 'Invalid phone/email';

			} else if (_error === 'shipping_issue') {
				msg = 'There was a problem with your shipping information';

			} else if (_error === 'billing_issue') {
				msg = 'There was a problem with your billing information';

            } else if ((_error === 'address_not_found') || (_error.toLowerCase().indexOf('address not found') > -1)) {
                msg = 'Address not found';

            } else if (_error.toLowerCase().indexOf('multiple addresses were found') > -1) {
                msg = 'Invalid address';

            } else if (_error.toLowerCase().indexOf('invalid city') > -1) {
                msg = 'Invalid city';

            } else if (_error.toLowerCase().indexOf('address you entered was found but more information is needed') > -1) {
                // Default address: The address you entered was found but more information is needed (such as an apartment, suite, or box number) to match to a specific address.
                msg = 'Address is missing information (such as an apartment, suite, or box number)';

            } else if (_error === 'sold_out_items') {
                msg = 'Oops, one or more of the items in your shopping bag is sold out. Please edit the item or delete it from your bag to complete your purchase.';

            } else if (_error === 'session_does_not_exist') {
                msg = 'Invalid Session';

            } else if (_error === 'password_do_not_match') {
                msg = 'The passwords you entered do not match';

            }

			return msg;
		},

		getInitials: function(full_name) {
		
			var initials = '';
			
			if (full_name) {
				var names = full_name.split(' ');
				initials = names[0].charAt(0) + names[1].charAt(0);
			}
			
			return initials;
		},

		generatePassword: function(data) {

			var password = '';
			
			if (data) {
				if ((data.phone) && (data.email)) {

					var phone = '';
					if (data.email.indexOf('allume.co') > -1) {
						phone = BH.Util.cleanPhone(data.phone.substr(0, 10));
					} else {
						phone = BH.Util.cleanPhone(data.phone);
					}

					var email_part = data.email.substring(0, data.email.indexOf('@')),
						email_part_mid_point = Math.floor(email_part.length / 2),
						email_part_first = email_part.substring(email_part_mid_point),
						email_part_second = email_part.substring(0, email_part_mid_point),
	
						phone_mid_point = Math.floor(phone.length / 2),
						phone_first = phone.substring(phone_mid_point),
						phone_second = phone.substring(0, phone_mid_point);

					password = phone_first + email_part_second + phone_second + email_part_first;
				}
			}
			
			return password;			
		},

        // Get the max length that does not break in the middle of a word 
        getActualMaxLength: function(copy, max_length) {

			var actual_max_length = max_length;
	        
	        if (copy.length > max_length) {
		        
				// If last character shown +1 is not a space, then go back until get to a space
				for (var i = max_length; i > 0; i--) {
					
					if (copy.charAt(i) === ' ') {
						actual_max_length = i;
						break;
					}
				}

	        }
	
	        return actual_max_length;
        },

		getAddToCartQty: function (cartItems, product_id, variant, qtyToAdd) {
			
			// Is this product/variation_info already in the cart?
			_.each(cartItems, function(item, idx) {

				if (!variant) {
					variant = '';					
				}

				if ((item.product_id === product_id) && (item.variation_info === variant)) {
					qtyToAdd = qtyToAdd + item.quantity;
				}
			});

			return qtyToAdd;
		},
		
		getCreditCardType: function(creditCardNumber) {
			
			var result = 'unknown';
			
			creditCardNumber = creditCardNumber || '';
					
		    if (creditCardNumber.match(new RegExp('^4[0-9]{0,15}$'))) {
		        result = 'visa';

		    } else if (creditCardNumber.match(new RegExp('^5$|^5[1-5][0-9]{0,14}$'))) {
		        result = 'mastercard';

		    } else if (creditCardNumber.match(new RegExp('^3$|^3[47][0-9]{0,13}$'))) {
		        result = 'amex';

		    } else if (creditCardNumber.match(new RegExp('^6$|^6[05]$|^601[1]?$|^65[0-9][0-9]?$|^6(?:011|5[0-9]{2})[0-9]{0,12}$'))) {
		        result = 'discover';
		    }
			
		    return result;
		},
		
		getModeParam: function() {
			
			var mode = (BH.Util.getParameterByName('m') !== null) ? BH.Util.getParameterByName('m') : '',
				modeParam = '';
			
			if (mode.length > 0) {
				modeParam = '&m=1';
			}
			
			return modeParam;
		},

		// Object.values does not work in Safari, so use this instead
		getObjectKeys: function(obj) {
        	var keys = [];
        	for (var p in obj) {
        		keys.push(p);
			}
			return keys;
		},
	    
	    // Get URL param by name
		getParameterByName: function(name) {
			
		    var url = window.location.href;
		    
		    name = name.replace(/[\[\]]/g, "\\$&");
	
		    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
		        results = regex.exec(url);
	
		    if (!results) return null;
		    if (!results[2]) return '';
	
			//return decodeURIComponent(results[2].replace(/\+/g, " "));
		    return decodeURIComponent(results[2]);
		},
	    
	    // Optional argument utms
	    getParametersByUTMs: function(utms) {
		    var url 	= '',
		    	_utms	= (typeof(utms) !== 'undefined') ? utms : BH.Util.getUTMs();
		    
		    if (_utms.campaign.length > 0) {
			    url = 'utm_campaign=' + _utms.campaign;
		    }

		    if (_utms.medium.length > 0) {
			    if (url.length > 0) {
				    url += '&utm_medium=' + _utms.medium;
				} else {
				    url = 'utm_medium=' + _utms.medium;
			    }
		    }
			
		    if (_utms.source.length > 0) {
			    if (url.length > 0) {
				    url += '&utm_source=' + _utms.source;
				} else {
				    url = 'utm_source=' + _utms.source;
			    }
		    }
		    
		    if (_utms.term.length > 0) {
			    if (url.length > 0) {
				    url += '&utm_term=' + _utms.term;
				} else {
				    url = 'utm_term=' + _utms.term;
			    }
		    }
		    
		    return url;
	    },
		
	    getUTMs: function() {

			var utm_campaign	= (BH.Util.getParameterByName('utm_campaign') !== null) ? BH.Util.getParameterByName('utm_campaign') : '',
				utm_medium 		= (BH.Util.getParameterByName('utm_medium') !== null) ? BH.Util.getParameterByName('utm_medium') : '',
				utm_source 		= (BH.Util.getParameterByName('utm_source') !== null) ? BH.Util.getParameterByName('utm_source') : '',
				utm_term 		= (BH.Util.getParameterByName('utm_term') !== null) ? BH.Util.getParameterByName('utm_term') : '',
				
			_utms = {
				'campaign': utm_campaign,
				'medium': utm_medium,
				'source': utm_source,
				'term': utm_term
			};

			// If no UTMs then check cookie
			if ( (_utms.campaign.length > 0) || (_utms.medium.length > 0) || (_utms.source.length > 0) || (_utms.term.length > 0) ) {

				// If any UTMs then save in cookie (for 30 days)
				Cookies.set('allume-utms', _utms, { domain: '.allume.co', expires: 30, path: '/', secure: true });

			} else {

				// If no UTMs then check cookie
				var utmsCookie = Cookies.getJSON('allume-utms');
				if ( (utmsCookie !== null) && (typeof(utmsCookie) !== 'undefined') ) {
					_utms = utmsCookie;
				}
				
			}

			return _utms;
	    },

		getTokenFromURL: function() {
	        var params = window.location.pathname.split('/').slice(1),
		        token = params[1];
	        
	        return token;
		},
		
	    getUSStateCodes: function() {
	        return [
	            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE',
	            'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA',
	            'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN',
	            'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM',
	            'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
	            'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA',
	            'WV', 'WI', 'WY'
// 	            'PR' 
// 	            'AS', 'FM', 'GU', 'MH', 'MP', 'PW', 'PR', 'AE', 'AA', 'AP', 'VI'
	        ];
	    },	
		
		getUSStates: function() {
	        return [
	            { "code": "AL", "name": "Alabama"},
	            { "code": "AK", "name": "Alaska"},
	            { "code": "AZ", "name": "Arizona"},
	            { "code": "AR", "name": "Arkansas"},
	            { "code": "CA", "name": "California"},
	            { "code": "CO", "name": "Colorado"},
	            { "code": "CT", "name": "Connecticut"},
	            { "code": "DE", "name": "Delaware"},
	            { "code": "DC", "name": "District of Columbia"},
	            { "code": "FL", "name": "Florida"},
	            { "code": "GA", "name": "Georgia"},
	            { "code": "HI", "name": "Hawaii"},
	            { "code": "ID", "name": "Idaho"},
	            { "code": "IL", "name": "Illinois"},
	            { "code": "IN", "name": "Indiana"},
	            { "code": "IA", "name": "Iowa"},
	            { "code": "KS", "name": "Kansas"},
	            { "code": "KY", "name": "Kentucky"},
	            { "code": "LA", "name": "Louisiana"},
	            { "code": "ME", "name": "Maine"},
	            { "code": "MD", "name": "Maryland"},
	            { "code": "MA", "name": "Massachusetts"},
	            { "code": "MI", "name": "Michigan"},
	            { "code": "MN", "name": "Minnesota"},
	            { "code": "MS", "name": "Mississippi"},
	            { "code": "MO", "name": "Missouri"},
	            { "code": "MT", "name": "Montana"},
	            { "code": "NE", "name": "Nebraska"},
	            { "code": "NV", "name": "Nevada"},
	            { "code": "NH", "name": "New Hampshire"},
	            { "code": "NJ", "name": "New Jersey"},
	            { "code": "NM", "name": "New Mexico"},
	            { "code": "NY", "name": "New York"},
	            { "code": "NC", "name": "North Carolina"},
	            { "code": "ND", "name": "North Dakota"},
	            { "code": "OH", "name": "Ohio"},
	            { "code": "OK", "name": "Oklahoma"},
	            { "code": "OR", "name": "Oregon"},
	            { "code": "PA", "name": "Pennsylvania"},
	            { "code": "RI", "name": "Rhode Island"},
	            { "code": "SC", "name": "South Carolina"},
	            { "code": "SD", "name": "South Dakota"},
	            { "code": "TN", "name": "Tennessee"},
	            { "code": "TX", "name": "Texas"},
	            { "code": "UT", "name": "Utah"},
	            { "code": "VT", "name": "Vermont"},
	            { "code": "VA", "name": "Virginia"},
	            { "code": "WA", "name": "Washington"},
	            { "code": "WV", "name": "West Virginia"},
	            { "code": "WI", "name": "Wisconsin"},
	            { "code": "WY", "name": "Wyoming"},
// 	            { "code": "AS", "name": "American Samoa"},
// 	            { "code": "FM", "name": "Federated States of Micronesia"},
// 	            { "code": "GU", "name": "Guam"},
// 	            { "code": "MH", "name": "Marshall Islands"},
// 	            { "code": "MP", "name": "Northern Mariana Islands"},
// 	            { "code": "PW", "name": "Palau"},
// 	            { "code": "PR", "name": "Puerto Rico"},
// 	            { "code": "AE", "name": "U.S. Armed Forces – Europe"},
// 	            { "code": "AA", "name": "U.S. Armed Forces – Americas"},
// 	            { "code": "AP", "name": "U.S. Armed Forces – Pacific"},
// 	            { "code": "VI", "name": "Virgin Islands"}
	        ];
		},
	    
		htmlEntitiesDecode: function(str) {
			if (str) {
				return str.replace(/&#(\d+);/g, function(match, dec) {
					return String.fromCharCode(dec);
				});
			} else {
				return str;
			}
		},
		
		// Polyfill for IE
		isInteger: function(value) {
			return typeof value === 'number' && isFinite(value) &&  Math.floor(value) === value;
		},		
		
	    isFreeTrial: function() {

			var isFreeTrial = false,
				UTMs = BH.Util.getUTMs();

			if ( (UTMs.campaign === 'fb_d_quizstart_prof_Pink2F') && (UTMs.medium === 'desktop_feed') && (UTMs.source === 'fb') ) {
				isFreeTrial = true;
			} else if ( (UTMs.campaign === 'fb_m_quizstart_prof_PinkF') && (UTMs.medium === 'mobile_feed') && (UTMs.source === 'fb') ) {
				isFreeTrial = true;
			} else if ( (UTMs.campaign === 'fb_m_quizstart_prof_Pink2F') && (UTMs.medium === 'mobile_feed') && (UTMs.source === 'fb') ) {
				isFreeTrial = true;
			}
	        
	        return isFreeTrial;
	    },

		isValidEmail: function(email) {
            var regEx = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
            	isValid = regEx.test(email);

			if (email) {
				if (email.indexOf('=') > -1) {
					isValid = false;
				}
			}

            return isValid;
		},
	    
	    isValidPhone: function(phone) {
            var regEx = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/igm;
            return regEx.test(phone);
	    },
	    
	    isValidUrl: function(url) {
		    var result = url.match(/(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g);
		    if (result === null) {
		        return false;
		    } else {
		        return true;
		    }
	    },
	    
		// 1250.223 => $1,250.22
		moneyFormat: function(value) {

            var floatValue = parseFloat(value).toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");

            if (floatValue > 0) {
                return '$' + floatValue;
            } else {
                return '-$' + (floatValue * -1).toFixed(2);
            }
		},

//		possibleOverrideFromInternalTool: function() {
//
//			var emailOverride = (BH.Util.getParameterByName('email') !== null) ? BH.Util.urlDecode(BH.Util.getParameterByName('email')) : '';
//
//			if (BH.Util.isValidEmail(emailOverride)) {
//
//				var env = (BH.properties.env === 'prod') ? 'prod' : 'stage';
//
//				//Cookies.set('allume-user-email-' + env,  BH.Util.urlDecode(emailOverride), { domain: '.allume.co', expires: 365, path: '/', secure: true });
//			}
//		},
		
		reportError: function(name, meta) {
			Bugsnag.notifyException(new Error(name), meta);
		},
		
        splitName: function(name) {
	        var names = name.trim().split(/\s+/),
	        	first_name = names[0];
	        
	        names.shift();

			return {
				first_name: first_name.trim(),
				last_name: names.join(' ').trim()
			};
        },
	    
        ucWords: function(str) {
			if (str) {
				return str.charAt(0).toUpperCase() + str.slice(1);
			} else {
				return str;
			}
        },
	        
		urlDecode: function(url) {
			return decodeURIComponent(url);
		},

		urlEncode: function(url) {
			return encodeURIComponent(url);
		}
	        
/*
        capitalize: function(items) {

	        var newItems = [];
	        
	        _.each(items, function(item, idx) {
		        newItems[idx] = item.replace(/\b\w/g, function(l) {
			        return l.toUpperCase()
			    });
	        });			

			return newItems;	        
        },
	
		var capitalize = function(str) {
		    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
		};
		
		var capitalizeEachWord = function(str) {
		
		    if (str) {
		
		        var words = str.split(' ');
		
		        for (var i = 0; i < words.length; i++) {
		            words[i] = capitalize(words[i]);
		        }
		
		        return words.join(' ');
		    }
		
		    return '';
		};
*/
    });

    if (!BH.Util) {
        BH.Util = new Util();
        BH.Util.render();
    }
});
