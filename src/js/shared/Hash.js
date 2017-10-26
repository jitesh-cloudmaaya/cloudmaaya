BH.add('Hash', function() {
	
	"use strict";
    eval(BH.System);

    var Hash = BH.Class(BH.Widget, {

        _init: function(node) {
            this.parent._init.call(this, node);
            this._ignoreHashChange = false;
            this._ignoreSetHash = false;

            this.set('changeEvent', new BH.Event());
        },

        _behavior: function() {
            var me = this;

            $(window).bind('hashchange', function() {
                if (!me._ignoreHashChange) {
                    me._ignoreSetHash = true;
                    me.get('changeEvent').fire(me.getHash());
                    me._ignoreSetHash = false;
                } else {
                    me._ignoreHashChange = false;
                }
            });
        },

        setHash: function(hash) {
            if (!this._ignoreSetHash) {
                this._ignoreHashChange = this.getHash() !== hash;
                window.location.hash = hash;
            }
        },

        getHash: function() {
            return window.location.hash.substring(1);
        }
    });

    if (!BH.Hash) {
        BH.Hash = new Hash($(window));
        BH.Hash.render();
    }
});