BH.add('LooksIndex', function() {
	
	"use strict";
    eval(BH.System);

    var LooksIndex = (function() {

        return BH.Class(BH.Widget, {

            _init: function(node, cfg) {
                this.parent._init.call(this, node);
	            this._cfg = cfg || {};

                this.set('state', new BH.Attr());

                this._is_fashionista = false;

                this.set('header', new BH.LooksHeader(this._node.find('.bh-id-looks-header')));
                this.set('intro', new BH.Intro(this._node.find('.bh-id-intro')));
                this.set('looks', new BH.Looks(this._node.find('.bh-id-looks')));
            },

            _render: function() {
	            this.parent._render.call(this);
	            var me = this;
	            
				this.get('header').render();
				this.get('intro').render();
				this.get('looks').render();

				this._setup();
            },
            
	        _behavior: function() {
				this.parent._behavior.call(this);
				var me = this;

	            this.get('state').sync(this.get('intro').get('state'));
	            this.get('state').sync(this.get('looks').get('state'));

	            this.on(this.get('state'), function(value) {

		            if (value === '') {

						BH.Hash.setHash('');
			            me.get('intro').hide();

		            } else if (value === 'intro') {
			            
			            me.get('intro').show();

                    } else if (value === 'fashionista') {

                        me._is_fashionista = true;
		            }
	            });

				this.on(BH.Hash.get('changeEvent'), function(hash) {
					me.get('state').set(hash);
				});

				// initial state (e.g. reload /looks/R72z4vpJGN24Bo5Mi2YsoB4eM3bKrJ6Y3tmsQNlWMHkjp/#intro)
				if (BH.Hash.getHash() === 'intro') {
					this.get('state').set('intro');
                } else if (BH.Hash.getHash() === 'fashionista') {
                    this.get('state').set('fashionista');
				} else {
					this.get('state').set('');
				}

	            this.on(this.get('looks').get('heartEvent'), function() {
					me.get('header').triggerEffect();
	            });
	        },
	        
	        _setup: function() {
		        var me = this;

                this.on(BH.GlobalEvents.get('setVisitorIdEvent'), function() {

                    if (BH.Util.getTokenFromURL().toString().length > 0) {

                        BH.StylingService.getStylingSession(
                            { 'token': BH.Util.getTokenFromURL() },
                            function(data) {

                                if (data) {
                                    me.get('intro').setData(data);

                                    data.is_fashionista = me._is_fashionista;
                                    me.get('looks').setData(data);

                                    me.get('looks').show();

                                    me.get('header').refresh();
                                }
                            }
                        );

                    } else {
                        BH.log('Missing styling session token');
                    }

                });

		        this.get('header').setStylingSessionToken(BH.Util.getTokenFromURL());
	        }

        });
    }());

    if (!BH.LooksIndex) {
		BH.LooksIndex = new LooksIndex($('body'));
		BH.LooksIndex.render();
    }
});
