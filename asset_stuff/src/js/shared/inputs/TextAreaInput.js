BH.add('TextAreaInput', function() {
	
	"use strict";
    eval(BH.System);

    var CharacterCountdown = BH.Class(BH.Widget, {
	    
        _init: function(node, cfg) {
            cfg = cfg || {};
            this.parent._init.call(this, node);

            this.set('characterCount', new BH.Attr());

            this._maxlength = cfg.maxlength;
            this._count = this._node.find('.bh-id-char-count');
        },

        _behavior: function() {
            this.parent._behavior.call(this);
            var me = this;

            this.on(this.get('characterCount'), function(v) {
                me._updateCount(v);
            });
        },

        _updateCount: function(v) {
            var left = this._maxlength - v;
            this._count.text(left);
            this._node.toggleClass('maxed-out', left === 0);
        }
    });

    var TextAreaInputChangeEvent = BH.Class(BH.Base, {
	    
        _init: function(node) {
            this.parent._init.call(this);
            this._node = node;
            this._status = 'stable'; // stable | changing

            this.set('changeEvent', new BH.Event());

            this._behavior();
        },

        _behavior: function() {
            var me = this;

            this._node.on('change', function() {
                if (me._status === 'stable') {
                    me.get('changeEvent').fire();
                    me._status = 'changing';
                    setTimeout(function() {
                        me._status = 'stable';
                    }, 200);
                }
            });

            this._node.on('blur', function() {
                if (me._status === 'stable') {
                    me.get('changeEvent').fire();
                } else {
                    me._status = 'stable';
                }
            });
        }
    });

    BH.TextAreaInput = BH.Class(BH.Widget, {
	    
        _init: function(node, cfg) {
            cfg = cfg || {};
            this.parent._init.call(this, node);

            this._placeHolder = cfg.placeHolder || '';
            //this._usePlaceholder = !Modernizr.input.placeholder;
            this._useCharCountdown = cfg.useCharCountdown && cfg.charCountdownNode || false;
            this._charCountdownNode = cfg.charCountdownNode || null;
            this._maxlength = cfg.maxlength || this._node.attr('maxlength') || 1024;

            this._status = 'empty'; // empty | filled

            this._validation = new BH.Validation();

            this.set('characterCount', new BH.Attr());

            this.set('textAreaInputChangeEvent', new TextAreaInputChangeEvent(this._node));
            this.set('changeEvent', new BH.Event());
            this.set('blurEvent', new BH.Event());
            this.set('focusEvent', new BH.Event());
            this.set('keyupEvent', new BH.Event());

            this.set('value', new BH.Attr());
        },

        _render: function() {
            this.parent._render.call(this);

            if(this._usePlaceholder) {
                this._node.attr('placeholder', this._placeHolder);
            }

            this._node.attr('maxlength', this._maxlength);
        },

        _behavior: function() {
            var me = this;
            this.parent._behavior.call(this);

            this.on(this.get('textAreaInputChangeEvent').get('changeEvent'), function(e) {
                me._change();
                me.get('changeEvent').fire();
            });

            this.on(this.get('value'), function(v){
                me._displayValue(v);
            });

            this._node.on('focus', function() {
                if (me._status === 'empty') {
                    me._node.val('').removeClass('placeholder');
                }
                me.get('focusEvent').fire();
            });

            this._node.on('blur', function() {
                // setTimeout(function() {
                if (me._usePlaceholder && me._status === 'empty') {
                    me._node.val(me._placeHolder).addClass('placeholder');
                }
                // }, 200);
                me.get('blurEvent').fire();
            });

            me._node.on('keyup', function() {
                me.get('keyupEvent').fire();
            });

            if(this._useCharCountdown) {
                this.set('characterCountdown', new CharacterCountdown(this._charCountdownNode, {
                    maxlength: this._maxlength
                }));
                this.get('characterCountdown').render();
                this.get('characterCount').sync( this.get('characterCountdown').get('characterCount') );

                this.on(this.get('keyupEvent'), function() {
                    me._updateCharCounter();
                });

                this.on(this.get('value'), function() {

                });

                this._updateCharCounter();
            }
        },

        _change: function() {
            var v = this._node.val();
            this.setData(v);
        },

        _displayValue: function(v) {
            var me = this;

            //if (v == null || v === '') {
            if (v === null || v === '') {
                me._status = 'empty';
                if (me._usePlaceholder) {
                    me._node.val(me._placeHolder).addClass('placeholder');
                }
            } else {
                me._status = 'filled';
                me._node.val(v);
            }
        },

        _updateCharCounter: function() {
            var str = this.getTransientData() || '',
                length = str.length,
                breaks = str.match(/[\n\r]/g);

            length += breaks ? breaks.length : 0;

            this.get('characterCount').set(length);
        },

        getData: function() {
            this._change();
            return this.get('value').get();
        },

        getTransientData: function() {
            return this._node.val();
        },

        setData: function(v) {
            if (v && v.length > this._maxlength){
                v = v.substr(0, this._maxlength);
            }
            
            //v = this._validate(v);
            this.get('value').set(v);
        },

        clear: function() {
            var me = this;
            me.clearError();
            this.get('value').set('');

            if (me._usePlaceholder) {
                me._node.val(me._placeHolder).addClass('placeholder');
            } else {
                me._node.val('');
            }

            this._updateCharCounter();
        },

        disable: function() {
            this._node.attr('readonly', 'readonly');
        },

        enable: function() {
            this._node.removeAttr('readonly');
        },

        isEmpty: function() {
            return !this.getData();
        },

        isEmptyTransient: function() {
            return !this.getTransientData();
        },

        focus: function() {
            this._node.focus();
        },

        getErrors: function() {
            return this._validation.getErrors();
        },

        hasErrors: function() {
            return this._validation.hasErrors();
        },

        clearError: function() {
            this._node.removeClass('field-error');
            this._validation.clearError();
        },

        addValidation: function(rule) {
            this._validation.addRule(rule);
        },

        validate: function() {
            var v = this.getData();
            this._validate(v);
        },

        _validate: function(v) {

            this._node.removeClass('field-error');
            this._validation.validate(v);
            if (this._validation.hasErrors()) {
                if (this._autoCorrectValue !== null) {
                    v = this._autoCorrectValue;
                    this._validation.validate(v);
                }
                this._node.addClass('field-error');
            }
            return v;
        },

        disableAutocomplete: function() {
            this._node.attr('autocomplete', 'off');
        },

        enableAutocomplete: function() {
            this._node.attr('autocomplete', 'on');
        }
    });

});