BH.add('GoogleAnalytics', function() {
	
	"use strict";
    eval(BH.System);

    var GoogleAnalytics = BH.Class(BH.Widget, {

        trackPageView: function(eventAction) {
            
			var eventCategory = '';

			// Move to BH.GoogleAnalytics?
			if ($.device.mobile()) {
				eventCategory = 'mobilePageView';
			} else {
				eventCategory = 'desktopPageView';
			}

			BH.GoogleAnalytics.trackEvent(eventCategory, eventAction);
        },

		trackEvent: function(category, action, label, value) {
			// https://developers.google.com/analytics/devguides/collection/analyticsjs/events
			
			var data = {
					'hitType': 'event',
					'eventCategory': category,
					'eventAction': action
				};

			if (label) {
				data.eventLabel = label;
			}		
				
			if (BH.Util.isInteger(parseInt(value))) {
				data.eventValue = parseInt(value);
			}

			ga('send', data);			
		}
		
    });

    if (!BH.GoogleAnalytics) {
        BH.GoogleAnalytics = new GoogleAnalytics($(window));
        BH.GoogleAnalytics.render();
    }
});