BH.add('SelectInput', function() {
	
	"use strict";
    eval(BH.System);

    BH.SelectInput = new BH.Class(BH.Widget, {
	    
        _init: function(node, cfg) {
            this.parent._init.call(this, node);
			this._cfg = cfg || {};
            
            this.set('changeEvent', new BH.Event());
            this.set('value', new BH.Attr());

            this._validation = new BH.Validation();
        },

        _render: function() {
            this.parent._render.call(this);

            if (this._cfg) {
	            this._setup();
            }
        },

        _behavior: function() {
            var me = this;

            this._node.on('change', function() {
                me._change();
                me.get('changeEvent').fire();
            });

            this._node.on('blur', function() {
                me._change();
                me.get('changeEvent').fire();
            });

            this.on(this.get('value'), function(v) {
                me._node.val(v);
            });
        },

        _change: function(){
            var v = this._node.val();
            this.setData(v);
        },

        addValidation: function(rule) {
            this._validation.addRule(rule);
        },

        getErrors: function() {
            return this._validation.getErrors();
        },

        _validate: function(v) {
            this.clearError();
            this._validation.validate(v);
            if (this._validation.hasErrors()) {
                this._node.addClass('field-error');
            }
            
            return v;
        },

        validate: function() {
            var v = this.getData();
            this._validate(v);
        },

        getTransientData: function() {
            return this._node.val();
        },

        getData: function() {
            this._change(); // Safari autofill fix
            return this.get('value').get();
        },

        clearError: function() {
            this._node.removeClass('field-error');
        },

        clear: function() {
            this.get('value').set(null);
            this.clearError();
        },

        setData: function(v) {
            v = this._validate(v);
            this.get('value').set(v);
        },

        hasErrors: function() {
            return this._validation.hasErrors();
        },

        disable: function() {
            this._node.attr('disabled', 'disabled');
        },

        enable: function() {
            this._node.removeAttr('disabled');
        },

        isEmptyTransient: function() {
            return !this.getTransientData();
        },

        disableAutocomplete: function() {
            this._node.attr('autocomplete', 'off');
        },

        enableAutocomplete: function(){
            this._node.attr('autocomplete', 'on');
        },

        focus: function() {
            if (!this._disabled) {
                this._node.focus();
            }
        },
        
        disableOption: function(value) {
	        
	        _.each(this._node.find('option'), function(item, key) {
		        	        
				var itemNode = $(item);
	        
				if (itemNode.text() === value) {
// 					itemNode.text(itemNode.text().replace(/\w/g, "$&\u0336"));
					itemNode.attr('disabled', 'disabled');
					//$("#list option[value='2']").text()
				}
	        });
        },
        
		enableAll: function() {
			
	        _.each(this._node.find('option'), function(item, key) {
				$(item).removeAttr('disabled');
	        });
		},
        
        _setup: function() {
	        
	        if ( (this._cfg) && (this._cfg.options) && (this._cfg.options.length > 0) ) {

		        var me = this,
		        	options = this._cfg.options,
		        	tpl = $('<option></option>');

				me._node.empty();

		        options.forEach(function(item, idx) {
			        var option = tpl.clone();
			        
					option.attr('value', item.id);
			        option.text(item.name);

			        if ( (me._cfg.defaultSelected) && (me._cfg.defaultSelected === item.id) ) {
				        option.attr('selected', 'selected');
			        }
			        
					me._node.append(option);
		        });
	        }
        },
        
        setOptions: function(options) {
	        
			var me = this,
	        	tpl = $('<option></option>');	        
	        
			this._node.empty();
	        
	        _.each(options, function(item) {
		        
		        var option = tpl.clone();
				option.attr('value', item);
		        option.text(item);
		        
				me._node.append(option);
	        });
        }

    });
});