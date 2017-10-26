BH.add('ErrorModal', function() {
	
	"use strict";
    eval(BH.System);

	// This widget uses src/html/partials/error_modal.html

    BH.ErrorModal = new BH.Class(BH.BaseCompositeInput, {
	    
        _init: function(node, cfg) {
            this.parent._init.call(this, node);
			this._cfg = cfg || {};

            this.set('hideEvent', new BH.Event());
			this.set('message', new BH.TextNode(this._node.find('.bh-id-message')));
			
            this.set('modal', new BH.Modal({
                autoCenter: true,
                closeButtons: this._node.find('.bh-id-close'),
                dismissable: true,
                node: this._node
            }));
        },

        _render: function() {
            this.parent._render.call(this);
        },

        _behavior: function() {
            var me = this;
			this.parent._behavior.call(this);

            this.on(this.get('modal').get('hideEvent'), function() {
                // If you do not use the X to close the modal then after the first time when you click outside the modal to close it the shade does not hide.
                // I don't have the time or the patience to figure this out right now.
                $('.modal-shade').addClass('hide');
                me.get('hideEvent').fire();
            });
        },
        
		setData: function(data) {
			this._data = data;
			
			if (data.message) {
				this.get('message').html(data.message);				
			}
		},
		
        show: function() {
			this.get('modal').show();
        }
    });
});