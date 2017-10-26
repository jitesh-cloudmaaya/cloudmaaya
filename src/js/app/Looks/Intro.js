BH.add('Intro', function() {
	
	"use strict";
    eval(BH.System);

    BH.Intro = BH.Class(BH.Widget, {

        _init: function(node, cfg) {
            this.parent._init.call(this, node);
            this._cfg = cfg || {};

            this.set('clientName', new BH.TextNode(this._node.find('.bh-id-client-name')));
            this.set('state', new BH.Attr());

            this.set('modal', new BH.Modal({
                closeButtons: this._node.find('.bh-id-close'),
                dismissable: true,
                node: this._node
            }));
        },

        _render: function() {
            this.parent._render.call(this);
            var me = this;
        },
        
        _behavior: function() {
			this.parent._behavior.call(this);
			var me = this;

            this.on(this.get('modal').get('exitEvent'), function() {

                me.get('state').set(''); // Go to looks

                Cookies.set('allume-' + BH.Util.getTokenFromURL(), 'shown', { domain: '.allume.co', expires: 90, path: '/', secure: true });
            });
        },
        
        setData: function(data) {
            this.get('clientName').text(data.client_first_name);
        },
        
        hide: function() {
	        this.get('modal').hide();
        },
        
        show: function() {

			// Has the intro modal already been shown for this styling session?
			var cookieName = 'allume-' + BH.Util.getTokenFromURL();
			
			if (Cookies.get(cookieName) && (Cookies.get(cookieName) === 'shown')) {
				this.get('state').set(''); // Go to looks
			} else {
		        this.get('modal').show();

	            BH.GoogleAnalytics.trackPageView('SeeLookIntroPage');
	            
				this.on(BH.GlobalEvents.get('setVisitorIdEvent'), function() {
		            BH.TrackingService.pageView('look-intro');
				});			
	            
			}
        }
    });
});
