BH.add('BaseCompositeInput', function() {
	
	"use strict";
    eval(BH.System);

    BH.BaseCompositeInput = new BH.Class(BH.Widget, {

        _init: function(node) {
            this.parent._init.call(this, node);

            this.set('_extendBehaviorEvent', new BH.Event());
            this.set('_extendHandleErrorsEvent', new BH.Event());
            this.set('_extendRenderEvent', new BH.Event());
            this.set('_extendValidateEvent', new BH.Event());

            this.set('blurEvent', new BH.Event());
            this.set('enterEvent', new BH.Event());
            this.set('updatedEvent', new BH.Event());

            this._errors = [];
        },

        _render: function() {
            this.get('_extendRenderEvent').fire();
        },

        _behavior: function() {
            var me = this;

            this.get('_extendBehaviorEvent').fire();
        },

        getErrors: function() {
            return this._errors;
        },

        hasErrors: function() {
            return this.getErrors().length !== 0;
        },

        validate: function() {
            this.get('_extendValidateEvent').fire();
            this._handleErrors();
        },

        _addInput: function(cfg) {
            var me = this,
                cls = cfg.cls,
                name = cfg.name,
                node = cfg.node,
                validationRules = cfg.validationRules || [],
                inputCfg = cfg.inputCfg,
                input,
                errors;

            this.set(name, new cls(node, inputCfg));
            input = this.get(name);

            this.on(this.get('_extendRenderEvent'), function() {
                input.render();
            });

            this.on(this.get('_extendBehaviorEvent'), function() {
	            
                $(validationRules).each(function(_, rule) {
                    input.addValidation(rule);
                });
                
                me.on(input.get('changeEvent'), function() {
                    me._handleErrors();
                    me.get('updatedEvent').fire();
                });
            });

            this.on(this.get('_extendHandleErrorsEvent'), function() {
                errors = input.getErrors();
                if (errors.length > 0) {
                    me._errors = me._errors.concat(errors);
                }
            });

            this.on(this.get('_extendValidateEvent'), function() {
                input.validate();
            });

            if (input.has('pressEnterEvent')) {
                this.on(input.get('pressEnterEvent'), function(e) {
                    me.get('enterEvent').fire(e);
                });
            }

            if (input.has('blurEvent')) {
                this.on(input.get('blurEvent'), function(e) {
                    me.get('blurEvent').fire();
                });
            }
        },

        _addCompositeInput: function(cfg) {
            var me = this,
                cls = cfg.cls,
                clsCfg = cfg.clsCfg,
                name = cfg.name,
                node = cfg.node,
                input,
                errors;

            this.set(name, new cls(node, clsCfg));
            input = this.get(name);

            this.on(this.get('_extendRenderEvent'), function() {
                input.render();
            });

            this.on(this.get('_extendBehaviorEvent'), function() {
                me.on(input.get('updatedEvent'), function(v) {
                    me._handleErrors();
                    me.get('updatedEvent').fire();
                });
            });

            this.on(this.get('_extendHandleErrorsEvent'), function() {
                errors = input.getErrors();
                if (errors.length > 0) {
                    me._errors = me._errors.concat(errors);
                }
            });

            this.on(this.get('_extendValidateEvent'), function() {
                input.validate();
            });

            if (input.has('enterEvent')) {
                this.on(input.get('enterEvent'), function(e) {
                    me.get('enterEvent').fire(e);
                });
            }

            if (input.has('blurEvent')) {
                this.on(input.get('blurEvent'), function(e) {
                    me.get('blurEvent').fire(e);
                });
            }
        },

        _handleErrors: function() {
            this.get('_extendHandleErrorsEvent').fire();
        },

        _handleError: function(input, parent, errorMsg) {
            var errors = input.getErrors(),
                len = errors.length;

            parent.removeClass('field-error invalid-field-error required-field-error');

            if (len > 0) {
                _(errors).each(function(error) {
                    parent.addClass(error.type + '-field-error');
                    if (error.type === 'invalid') {
                        errorMsg.text(error.message);
                    } else {
                        errorMsg.text('');
                    }
                });
            }
        },

        show: function() {
            this._node.removeClass('hide');
        },

        hide: function() {
            this._node.addClass('hide');
        }
    });
});
