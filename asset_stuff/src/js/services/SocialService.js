BH.add('SocialService', function() {
	
	"use strict";
    eval(BH.System);

	// REF: https://github.com/allumestyle/social-services/blob/master/social_actions/templates/test.html

    var SocialService = BH.Class(BH.Widget, {
	    
		getCommentsForLooksInASession: function(data, successCb, errorCb) {
            // If returns error then session does not exist.

		    BH.BaseService._get(
		    	data,
				BH.properties.socialServiceAjaxHost + '/social_actions/fetch_looks_social_actions_for_session/',
				function(responseData) {
					if (successCb) {
						successCb(responseData);
					}
				},
				errorCb
			);
		},	    
		
		getHeartedProducts: function(data, successCb, errorCb) {

		    BH.BaseService._get(
		    	data,
				BH.properties.socialServiceAjaxHost + '/social_actions/fetch_hearted_product_details_for_session/',
				function(responseData) {
					if (successCb) {

						var groupedProducts = _.groupBy(responseData, 'product_id'),
							products = [];

						for (var product_id in groupedProducts) {
							products.push(BH.StylingService.getProductStructuredData(groupedProducts[product_id]));	
						}
		
						successCb(_.sortBy(products, 'product_name'));
					}
				},
				errorCb
			);
		},	    
	    
		// Get heart state and all comments for products in the given Look
		getSocialData: function(data, successCb, errorCb) {

		    BH.BaseService._get({
					look_id: data.look_id
				},
				BH.properties.socialServiceAjaxHost + '/social_actions/fetch_for_look_products/',
				function(responseData) {
					if (successCb) {
						successCb(responseData);
					}
				},
				errorCb
			);
		},

		// Toggle heart
		addOrUpdateHeart: function(data, successCb, errorCb) {

		    BH.BaseService._get({
					action: 'hearted',
					action_value: data.action_value + '',
					object: data.object, // 'look' | 'product'
					object_id: data.object_id, // data.look_id | data.product_id
					context: 'look',
					context_id: data.look_id
				},
				BH.properties.socialServiceAjaxHost + '/social_actions/add_or_update/',
				function(responseData) {
					if (successCb) {
						successCb(responseData);
					}
				},
				errorCb
			);
		},	    

		// Toggle star
/*
		addOrUpdateStar: function(data, successCb, errorCb) {
			
		    BH.BaseService._get({
					action: 'starred',
					action_value: data.action_value + '',
					object: 'look',
					object_id: data.look_id,
					context: 'look',
					context_id: data.look_id
				},
				BH.properties.socialServiceAjaxHost + '/social_actions/add_or_update/',
				function(responseData) {
					if (successCb) {
						successCb(responseData);
					}
				},
				errorCb
			);
		},
*/
		
		addOrUpdateComment: function(data, successCb, errorCb) {
			
		    BH.BaseService._get({
					action: 'commented',
					action_value: data.action_value,
					object: data.object, // 'look' | 'product'
					object_id: data.object_id, // data.look_id | data.product_id
					context: 'look',
					context_id: data.look_id
				},
				BH.properties.socialServiceAjaxHost + '/social_actions/add_or_update/',
				function(responseData) {
					if (successCb) {
						successCb(responseData);
					}
				},
				errorCb
			);
		}

    });

    if (!BH.SocialService) {
        BH.SocialService = new SocialService();
        BH.SocialService.render();
    }
});
