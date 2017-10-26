BH.add('ImageView', function() {
	
	"use strict";
    eval(BH.System);
    
    // Just like iOS! :)
    // HTML: <div class="bh-id-image image image-view collage"></div>
	// indicate the type of image by using the "collage" or "piece" class

    BH.ImageView = new BH.Class(BH.Widget, {
	    
        _init: function(node, cfg) {
            this.parent._init.call(this, node);
			this._cfg = cfg || {};
			
			this.set('clickEvent', new BH.Event());
			this.set('swipeLeftEvent', new BH.Event());
			this.set('swipeRightEvent', new BH.Event());
        },

        _render: function() {
            this.parent._render.call(this);
        },

        _behavior: function() {
            var me = this;

			this._node.on('click', function() {

                // This is probably all overkill, but I was not exactly able to reproduce the error...
                me._data.url = null;

                var data = {};
                if (typeof(me._data) !== 'undefined') {
                    data = me._data;
                }

                if (!data) {
                    data = {};
                }

                if (data.url) {
                    me.get('clickEvent').fire(data.url);
                } else {
                    me.get('clickEvent').fire();
                }
			});
        },
        
		clear: function() {
			this._node.find('img').remove();			
		},
        
        setData: function(data) {
	        var me = this;
	        
	        this._data = data;
	        
	        if (data.url) {
		        if (BH.Util.isValidUrl(data.url)) {

			        this._node.append($('<img src="' + data.url + '" class="img-responsive" />'));
			        this._image = this._node.find('img');

			        this._image.removeClass('hide');

					this._node.on('swipeleft', function(event) {
						event.preventDefault();

						if ($.device.mobile()) {
							me.get('swipeLeftEvent').fire();
						}
					});

					this._node.on('swiperight', function(event) {
						event.preventDefault();

                        if ($.device.mobile()) {
							me.get('swipeRightEvent').fire();
						}
					});
		        }
	        }
        },
        
        setImageUrl: function(url) {
	        
	        if (url) {
		        if (BH.Util.isValidUrl(url)) {
					this._image.attr('src', url);
					this._data.url = url;
				}		        
	        }
        }

    });
});