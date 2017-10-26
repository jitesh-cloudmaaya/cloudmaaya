/*
BH.add('Rate', function() {
	
	"use strict";
    eval(BH.System);

	// This widget used html/templates/partials/rate.html

    var Star = BH.Class(BH.Widget, {

        _init: function(node, cfg) {
            this.parent._init.call(this, node);
            this._cfg = cfg || {};
            
            this._value = null;
            
            this.set('clickEvent', new BH.Event());
        },

        _render: function() {
            this.parent._render.call(this);
        },

        _behavior: function() {
            this.parent._behavior.call(this);
            var me = this;

            this._node.on('click', function() {
	            me.get('clickEvent').fire(me._value);
            });
        },
        
        setData: function(value) {
	        this._value = value;
        },
        
        getData: function() {
	        return this._value;
        },
        
        toggle: function(on) {
	        if (on) {
		        this._node.addClass('glyphicon-star').removeClass('glyphicon-star-empty');
		    } else {
		        this._node.addClass('glyphicon-star-empty').removeClass('glyphicon-star');
	        }
        }
    });   

    BH.Rate = new BH.Class(BH.Widget, {
	    
        _init: function(node, cfg) {
            this.parent._init.call(this, node);
			this._cfg = cfg || {};
			
            this._starList = this._node;
            this._starTpl = this._node.find('.bh-id-star-tpl').removeClass('bh-id-star-tpl hide').remove();
            
            this.set('rateEvent', new BH.Event());
            this.set('stars', new BH.List());
        },

        _render: function() {
            this.parent._render.call(this);
            
            this._setup();
        },

        _behavior: function() {
            var me = this;
        },

        _setup: function() {
	        var me = this;
	        
			// Products
		    this.clear();
			
			for (var i = 0; i < this._cfg.max; i++) {
				
				var node = me._starTpl.clone(),
					star = new Star(node, this._cfg);
					
            	star.render();
            	star.setData(i+1);
            	
            	me._starList.append(node);
            	me.get('stars').add(star);
            	
	            me.on(star.get('clickEvent'), function(rating) {
					me.setRating(rating);
					me.get('rateEvent').fire(rating);
	            });
			}
        },
        
        clear: function() {
            this.get('stars').clear();
            this._starList.empty();
        },
        
        setRating: function(rating) {
	        
	        this.get('stars').each(function(star, idx) {
		        
		        if (star.getData() <= rating) {
			        star.toggle(true);
				} else {
			        star.toggle(false);
		        }
	        });
        }
        
    });
});
*/