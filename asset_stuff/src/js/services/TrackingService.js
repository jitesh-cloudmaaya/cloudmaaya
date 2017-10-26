BH.add('TrackingService', function() {
	
	"use strict";
    eval(BH.System);

    var TrackingService = BH.Class(BH.Widget, {
	    
	    pageView: function(pageName, context_id, styling_session_token) {
		    
		    if (!context_id) {
			    context_id = '';
		    }

		    if (!styling_session_token) {
			    styling_session_token = '';
		    }

		    BH.BaseService._get(
				{
					info_id: context_id, // optional
					page: pageName,
					referrer: document.referrer,
					styling_session_token: styling_session_token, // optional
					url: window.location.href
				},
				BH.properties.trackingServiceAjaxHost + '/tracking_actions/track_page_views/'
			);
	    }

    });

    if (!BH.TrackingService) {
        BH.TrackingService = new TrackingService();
        BH.TrackingService.render();
    }
});
