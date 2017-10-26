BH.add('StylingService', function() {
	
	"use strict";
    eval(BH.System);

    var StylingService = BH.Class(BH.Widget, {

        addressVerification: function(data, successCb, errorCb) {

            BH.BaseService._get(
                data,
                BH.properties.stylingServiceAjaxHost + '/commerce-service/address-verification/',
                function(responseData) {
                    if (successCb) {
                        successCb(responseData);
                    }
                },
                errorCb,
                false // Don't JSON.stringify
            );
        },

	    /* BEGIN Quiz APIs */
		getNext: function(data, successCb, errorCb) {
			var me = this,
				serviceUrl = BH.properties.stylingServicePythonAjaxHost + '/quiz/get_next/';
			
			if (data.get_next_unfinished_step) {
				serviceUrl = BH.properties.stylingServicePythonAjaxHost + '/quiz/get_next_unfinished_step/';
			}
			
		    BH.BaseService._get(
				data,
				serviceUrl,
				function(responseData) {
					if (successCb) {

						if (data.get_next_unfinished_step) {
							if ((responseData.incomplete_quiz_in_other_device) && (!responseData.has_user_email_paid_styling_fee)) {
								BH.GlobalEvents.get('incompleteQuizInOtherDeviceEvent').fire();
							}
						}

						successCb(responseData);
					}
				},
				errorCb
			);
		},

		getPrevious: function(data, successCb, errorCb) {
			var me = this;

		    BH.BaseService._get(
				data,
				BH.properties.stylingServicePythonAjaxHost + '/quiz/get_previous/',
				function(responseData) {
					if (successCb) {
						successCb(responseData);
					}
				},
				errorCb
			);
		},
		
		isUserLoggedIn: function(successCb, errorCb) {
			var me = this;

		    BH.BaseService._get(
				{},
				BH.properties.stylingServicePythonAjaxHost + '/quiz/is_user_logged_in/',
				function(responseData) {
					if (successCb) {
						successCb(responseData);
					}
				},
				errorCb
			);
		},		
		
		// https://github.com/allumestyle/styling-service/blob/master/web/quiz_app/apis.py
		saveUserAnswer: function(data, successCb, errorCb) {
			var me = this;
			
			if (data) {

			    BH.BaseService._get(
					data,
					BH.properties.stylingServicePythonAjaxHost + '/quiz/save_user_answer/',
					function(responseData) {
						if (successCb) {
							successCb(responseData);
						}
					},
					errorCb
				);

			} else {
				if (errorCb) {
					errorCb();
				}
			}
			
		},

		uploadUserPhoto: function(formData, successCb, errorCb) {
			var me = this;
	
			$.ajax({
				crossDomain: true,
				xhrFields: {
					withCredentials: true
				},
		        cache: false,
		        contentType: false, // Set content type to false as jQuery will tell the server its a query string request
		        data: formData,
		        dataType: 'json',
		        processData: false, // Don't process the files
				type: 'POST',
		        url: BH.properties.stylingServicePythonAjaxHost + '/quiz/upload_user_photo/'

			}).done(function(response) {
				
				if ((response.code === 'ok') || (response.status === 'success')) {
					successCb(response.data);
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
					BH.log('FAIL (upload_user_photo)', error);
				}

			});			
		},
	    /* END Quiz APIs */

	    postPayment: function(data, successCb, errorCb) {
		    
		    BH.BaseService._get(
				data,
				BH.properties.stylingServiceAjaxHost + '/user-service/post-payment/',
				function(responseData) {
					if (successCb) {
						successCb(responseData);
					}
				},
				errorCb,
				false // Don't JSON.stringify
			);
	    },

        assignJobsToStylist: function(data, successCb, errorCb) {

            BH.BaseService._get(
                data,
                BH.properties.stylingServicePythonAjaxHost + '/assign_jobs_to_stylist/',
                function(responseData) {
                    if (successCb) {
                        successCb(responseData);
                    }
                },
                errorCb, true);
        },

	    postQuiz: function(data, successCb, errorCb) {
		    
		    BH.BaseService._get(
				data,
				BH.properties.stylingServiceAjaxHost + '/user-service/post-quiz/',
				function(responseData) {
					if (successCb) {
						successCb(responseData);
					}
				},
				errorCb,
				false // Don't JSON.stringify
			);
	    },

	    payStylingFee: function(data, successCb, errorCb) {

		    BH.BaseService._get(
				data,
				BH.properties.stylingServiceAjaxHost + '/commerce-service/purchase/',
				function(responseData) {
					if (successCb) {
						successCb(responseData);
					}
				},
				errorCb,
				false // Don't JSON.stringify
			);
	    },

		getProduct: function(data, successCb, errorCb) {
			var me = this;
			
		    BH.BaseService._get(
				data,
				BH.properties.stylingServiceAjaxHost + '/styling-session-service/get-product/',
				function(responseData) {
					if (successCb) {
						successCb(me.getProductStructuredData(responseData));
					}
				},
				errorCb,
				false // Don't JSON.stringify
			);
		},
	    
		getStylingSession: function(data, successCb, errorCb) {
			var me = this;
			
		    BH.BaseService._get(
				data,
				BH.properties.stylingServiceAjaxHost + '/styling-session-service/get-styling-sessions/',
				function(responseData) {
					if (successCb) {
						successCb(me._getStylingSessionStructuredData(responseData));
					}
				},
				errorCb,
				false // Don't JSON.stringify
			);
		},

        send_welcome_email: function(data, successCb, errorCb) {

            BH.BaseService._get(
                data,
                BH.properties.stylingServiceAjaxHost + '/client-service/send-welcome-email/',
                function(responseData) {
                    if (successCb) {
                        successCb(responseData);
                    }
                },
                errorCb,
				false // Don't JSON.stringify
			);
        },

	    setStylingFeeStatus: function(data, successCb, errorCb) {

		    BH.BaseService._get(
				data,
				BH.properties.stylingServiceAjaxHost + '/client-service/set-styling-fee-status/',
				function(responseData) {
					if (successCb) {
						successCb(responseData);
					}
				},
				errorCb,
				false // Don't JSON.stringify
			);
	    },

	    processStripeError: function (error, cb) {
		    
		    var msg = null;

			if (error) {
				
				if (error.code) {
					if (error.code === 'invalid_token') {
	
						if (error.data) {
							if (error.data.stripeCode) {
								
								if (error.data.stripeCode === 'incorrect_zip') {
									msg = 'Incorrect Zip';
									
								} else if (error.data.stripeCode === 'incorrect_cvc') {
									msg = 'Incorrect CVV';

								} else if (error.data.stripeCode === 'card_declined') {
									msg = 'Card Declined';
									
								} else if (error.data.stripeCode === 'expired_card') {
									msg = 'Expired Card';
									
								} else if (error.data.stripeCode === 'processing_error') {
									
									if (error.data.jsonBody) {
										if (error.data.jsonBody) {
											if (error.data.jsonBody.error) {
												if (error.data.jsonBody.error.message) {
													msg = error.data.jsonBody.error.message; // An error occurred while processing your card. Try again in a little bit.
												}										
											}										
										}										
									}

									if (msg === null) {
										msg = BH.Constants.DEFAULT_ERROR_MESSAGE;
									}
								}
								
							}						
						}
	
					}		    
				}

			}

		    if (cb) {
			    cb(msg);
		    }
	    },

		getProductStructuredData: function(data) {

			if (data.length > 0) {
				
				// Alternate images					        
		        var alternateImages = [];
		        _.each(data, function(item, idx) {
			        alternateImages[idx] = {
				        'image_color': item.alt_product_image_color,
				        'image_size': item.alt_product_image_size,
				        'image_url': item.alt_product_image_url
			        };
		        });

				var colors = null,
					sizes = null,
					color_sizes = null;

				if (data[0].size_color_info) {

					var size_color_info = JSON.parse(data[0].size_color_info);
					
					if ((size_color_info) && (size_color_info != "false")) {
				        colors = size_color_info.color.value.split(' | ').sort();
				        color_sizes = size_color_info['color-size'].value.split(' | '); // Valid color/size combos
						sizes = size_color_info.size.value.split(' | ');				
					}				

				}

				// Hearted or unhearted		        
		        var hearted = false;
		        if (data[0].social_action) {
			        if ((data[0].social_action === 'hearted') && (data[0].social_action_value === '1')) {
				        hearted = true;
			        }
		        }
		        
				var newData = {
						'alternate_images': alternateImages,
						'colors': colors,
						'color-size': color_sizes,
                        'external_url': data[0].external_url,
						'hearted': hearted,
                        'in_stock': data[0].in_stock,
						'look_id': data[0].look_id,
						'product_brand': data[0].product_brand,
						'product_descrip': data[0].product_descrip,
						'product_id': data[0].product_id,
						'product_image': data[0].product_image,
						'product_name': data[0].product_name,
						'product_price': data[0].product_price,
						'product_retailer': data[0].product_retailer,
						'product_sale_price': data[0].product_sale_price,
						'product_token': data[0].product_token,
						'return_policy': data[0].return_policy,
						'shipping_policy': data[0].shipping_policy,
						'sizes': sizes,
                        'tips': data[0].tips
				};

				if (data[0].look_token) {
					newData.look_token = data[0].look_token;
				}

		        return newData;
				
			} else {
				return {};
			}
		},
		
		_getStylingSessionStructuredData: function(data) {
			
	        var me = this,
		        looks = _.groupBy(data, 'look_id'),
	        	newDataLooks = {},
	        	products = _.groupBy(data, 'look_id');
			
			_.each(looks, function(look) {

//				newDataLooks[look[0].look_id] = BH.Util.filterObject(look[0], ['hearted', 'look_collage', 'look_descrip', 'look_id', 'look_last_modified', 'look_name', 'look_token', 'rating', 'stylist_first_name']);
                newDataLooks[look[0].look_id] = BH.Util.filterObject(look[0], ['hearted', 'look_collage', 'look_descrip', 'look_id', 'look_last_modified', 'look_name', 'look_token', 'rating']);

				newDataLooks[look[0].look_id].products = {};
			});
				
			for (var look_id in products) {
					
				var look_products = products[look_id];
				_.each(look_products, function(product) {

//					var filteredProduct = BH.Util.filterObject(product, ['product_brand', 'product_descrip', 'product_id', 'product_image', 'product_name', 'product_price', 'product_retailer', 'product_sale_price', 'product_token']);
                    var filteredProduct = BH.Util.filterObject(product, ['product_brand', 'product_id', 'product_image', 'product_name', 'product_price', 'product_retailer', 'product_sale_price', 'product_token']);

					newDataLooks[product.look_id].products[filteredProduct.product_id] = filteredProduct;
				});
			}

			var _products = _.groupBy(data, 'product_id');
			
			for (var look_name in newDataLooks) {
				for (var product_id in newDataLooks[look_name].products) {

					if (product_id !== 'undefined') {

//						var size_color_info = JSON.parse(Object.keys(_.groupBy(_products[product_id], 'size_color_info'))[0]);
//
//						var colors = null,
//							color_sizes = null,
//							piece = newDataLooks[look_name].products[product_id],
//							sizes = null;
						var piece = newDataLooks[look_name].products[product_id];

//						if ((size_color_info) && (size_color_info != "false")) {
//							colors = size_color_info.color ? size_color_info.color.value.split(' | ').sort() : [];
//							color_sizes = size_color_info['color-size'] ? size_color_info['color-size'].value.split(' | ') : []; // Valid color/size combos
//							sizes = size_color_info.size ? size_color_info.size.value.split(' | ') : [];
//						}
	
						// Alternate images
						var altImages = _.groupBy(_products[product_id], 'image_name')['undefined'],
							alternate_images = [];
						_.each(altImages, function(atlImage, idx) {
							alternate_images[idx] = BH.Util.filterObject(atlImage, ['image_color', 'image_size', 'image_url']);
						});
						piece.alternate_images = alternate_images;
	
//						//piece.colors = BH.Util.capitalize(colors); // May screw up color/size check and adding to cart?
//						piece.colors = colors;
//
//						piece['color-size'] = color_sizes;
//
//						//piece.sizes = this._sortSizes(sizes); // May screw up color/size check and adding to cart?
//						piece.sizes = sizes;
						
					} else {
						BH.log('ERROR: invalid data');
					}

				}
			}
			
			var sortedNewDataLooks = _.sortBy(newDataLooks, 'look_last_modified');
			sortedNewDataLooks = sortedNewDataLooks.reverse();

			var newData = {
				'client_first_name': '',  
				'client_last_name': '',
				'looks': sortedNewDataLooks,
//				'stylist_first_name': '',
//				'styling_session_end_date': null,
				'styling_session_id': 0,  
//				'styling_session_name': '',
//				'styling_session_start_date': null,
				'styling_session_token': ''
			};
			
			if (typeof(data[0]) != 'undefined') {
				
		        newData = {
			      'client_first_name': data[0].client_first_name,  
			      'client_last_name': data[0].client_last_name,
			      'looks': sortedNewDataLooks,
//			      'stylist_first_name': data[0].stylist_first_name,
//			      'styling_session_end_date': data[0].styling_session_end_date,
			      'styling_session_id': data[0].styling_session_id,  
//			      'styling_session_name': data[0].styling_session_name,
//			      'styling_session_start_date': data[0].styling_session_start_date,
			      'styling_session_token': data[0].styling_session_token
		        };
			}
							        
	        return newData;
		},
		
		_getAttribute: function(values, id_property, name_property) {
			var _values = {};

			for (var attribute_name in values) {
				
				var id = values[attribute_name][0][id_property],
					name = values[attribute_name][0][name_property];
					
				_values[id] = name;
			}
			
			return _values;			
		}

    });

    if (!BH.StylingService) {
        BH.StylingService = new StylingService();
        BH.StylingService.render();
    }
});
