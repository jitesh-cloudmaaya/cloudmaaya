BH.add('Button', function() {
	
	"use strict";
    eval(BH.System);

    BH.Button = new BH.Class(BH.Widget, {

        _init: function(node, cfg) {
            cfg = cfg || {};

            this.parent._init.call(this, node);
            this._allowDefault = cfg.allowDefault || false;
            this._allowDefaultOnMetaKey = cfg.allowDefaultOnMetaKey || false;
            this._buttonText = this._node.find('.bh-id-button-text');
            this._disabled = cfg.disabled || false;

            this.set('clickEvent', new BH.Event());
        },

        _behavior: function() {
            var me = this;

            this._node.on('click', function(e) {

                if (me._allowDefaultOnMetaKey && e.metaKey) {
                    return true;
                }

                if (!me._allowDefault) {
                    e.preventDefault();
                }

                if (me._disabled) {
                    return false;
                }

                me.get('clickEvent').fire(e);
            });
        },

        disable: function() {
            this._disabled = true;
            this._node.addClass('disabled');
        },

        enable: function() {
            this._disabled = false;
            this._node.removeClass('disabled');
        },

        toggleProcessing: function(on) {
            if (on) {
                this.disable();
                this._node.addClass('processing');
            } else {
                this.enable();
                this._node.removeClass('processing');
            }
        },

        isEnabled: function() {
            return !this._disabled;
        },

        setButtonText: function(text) {
            this._buttonText.text(text);
        },

        setContent: function(content) {
            this._node.html(content);
        },

        setHref: function(href) {
            if (this._node.is('a')) {
                this._node.attr('href', href);
            } else {
                this._node.find('a').attr('href', href);
            }
        }
    });
});