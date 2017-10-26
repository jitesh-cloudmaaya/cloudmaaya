BH.add('Heart', function() {
	
	"use strict";
    eval(BH.System);

    BH.Heart = new BH.Class(BH.Widget, {
	    
        _init: function(node, cfg) {
            this.parent._init.call(this, node);
			this._cfg = cfg || {};
			
			this._on = 0; // 1 | 0
			
			this.set('clickEvent', new BH.Event());
        },

        _render: function() {
            this.parent._render.call(this);
        },

        _behavior: function() {
            var me = this;
            
			this._node.on('click', function() {
				me.toggle();
				me.get('clickEvent').fire();
			});            
        },
        
        toggle: function() {
	    
			if (this._on) {
				this._node.attr('src', '/img/looks/heart_gray.png');
				this._on = 0;
			} else {
				this._node.attr('src', '/img/looks/heart_blush.png');
				this._on = 1;
			}
        },

        getData: function() {
	        
	        if (this._node.attr('src').indexOf('heart_blush') > -1) {
		        return 1;
	        } else {
		        return 0;
	        }
        },
        
        setToggle: function(on) {
	    
	    	// Better way to combing setToggle() and toggle()?    
	        if (on) {
		        this._node.attr('src', '/img/looks/heart_blush.png');
				this._on = 1;
		    } else {
			    this._node.attr('src', '/img/looks/heart_gray.png');
				this._on = 0;
	        }
        }
        
    });
});