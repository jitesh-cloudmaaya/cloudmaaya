BH.add('Modal', function() {

	"use strict";
    eval(BH.System);

    var Escape = new BH.Class(BH.Base, {

        _init: function() {
            this.parent._init.call(this);

            var me = this;

            this.set('pressEvent', new BH.Event());

            this._handler = function(e) {
                if (e.keyCode === 27) {
                    me.get('pressEvent').fire();

                }
            };
        },

        on: function() {
            $(window).on('keydown', this._handler);
        },

        off: function() {
            $(window).off('keydown', this._handler);
        }
    });

    BH.Modal = new BH.Class(BH.Base, {

        _init: function(options) {
            this._node = options.node;

            this.parent._init.call(this, this._node);

            this.isVisible = !this._node.hasClass('hide');

            this._closeButtons = options.closeButtons;

			/*jshint -W041 */            
            this._dismissable = options.dismissable != false;
			/*jshint -W041 */

            this._autoCenter = options.autoCenter || false;
            this._escape = new Escape();
            this._fade = options.fade;
            this._keepModalShade = false;
            this._startHidden = options.startHidden;

            this.set('exitEvent', new BH.Event());
            this.set('hideEvent', new BH.Event());
            this.set('showEvent', new BH.Event());

            this._render();
            this._behavior();
        },

        _render: function() {
            var me = this;

            if (me._startHidden && me._isVisible) {
                me.hide();
            }
        },

        _behavior: function() {
            var me = this;

            if (!$.device.mobile()) {
                BH.ModalShade.get('clickEvent').addListener(function(e) {
                    if (me.isVisible && me._dismissable === true) {
                        if (!$.device.ipad()) {
                            me.hide();
                            me.get('exitEvent').fire();
                        }
                    }
                });
            }

            this.on(this._escape.get('pressEvent'), function() {
                if (me.isVisible && me._dismissable) {
                    me.hide();
                    me.get('exitEvent').fire();
                }
            });

            if (this._closeButtons) {
				this._closeButtons.on('click', function(e) {
				    e.preventDefault();
				    if (me.isVisible && me._dismissable) {
				        me.hide();
				        me.get('exitEvent').fire();
				    }
				});
            }

            this._node.on('focusout', function() {
                setTimeout(function() {
                    if (me._node.find(':focus').length === 0) {
                        me.scrollTo();
                    }
                }, 0);
            });
        },

        setKeepModalShade: function(keep) {
            var me = this;
            me._keepModalShade = keep;
        },

        show: function() {
            var me = this;

            if (!this.isVisible) {
                this.isVisible = true;

                if (me._fade) {
                    this._node.fadeIn('fast');
                } else {
                    this._node.removeClass('hide');
                }

                if (this._autoCenter) {
                    this._node.addClass('auto-center');
                    this.setInCenterOfPage();
                }

                BH.ModalShade.show();

                this.get('showEvent').fire();

                this._escape.on();

                this.scrollTo();
            }
        },

        setInCenterOfPage: function() {

            var me = this,
                body = $('body'),
                viewHeight = body.height(),
                viewWidth = body.width(),
                overlayHeight = parseFloat(this._node.outerHeight(true)), // IMPORTANT! removeClass('hide') before setInCenterOfPage() or will not get a proper height
                overlayWidth = this._node.outerWidth(true);

            if ($.device.mobile()) {
                viewHeight = window.screen.height;
            }

            // I know this is weird, but I have center the modal twice or else it does not work?

            // Inside setTimeout 0 else will get incorrect this._node.outerHeight(true)
            setTimeout(function() {

                overlayHeight = me._node.outerHeight(true);
                overlayWidth = me._node.outerWidth(true);

                var scrollTop = body.scrollTop(),
                    overlayLeft = (viewWidth / 2) - (overlayWidth / 2),
                    overlayTop = (viewHeight / 2) - (overlayHeight / 2) + scrollTop;

                me._node.css('left', overlayLeft + 'px');
                me._node.css('top', overlayTop + 'px');

            }, 0);

            var scrollTop = body.scrollTop(),
                overlayLeft = (viewWidth / 2) - (overlayWidth / 2),
                overlayTop = (viewHeight / 2) - (overlayHeight / 2) + scrollTop;

            this._node.css('left', overlayLeft + 'px');
            this._node.css('top', overlayTop + 'px');
        },

        scrollTo: function() {
            if (this._node.css('position') !== 'fixed') {
                scrollTo(this._node, {
                    offset: $.device.mobile() ? -10 : 0
                });
            }
        },

        hide: function() {
            var me = this;

            if (this.isVisible) {
                this.isVisible = false;
                if (me._fade) {
                    this._node.fadeOut('fast');
                } else {
                    this._node.addClass('hide');
                }

                if (!this._keepModalShade) {
                    BH.ModalShade.hide();
                }

                this.get('hideEvent').fire();

                this._escape.off();
            }
        },

        disableExit: function() {
            this._dismissable = false;
            this._node.find('.close, .close-button').addClass('hide');
        },

        enableExit: function() {
            this._dismissable = true;
            this._node.find('.close, .close-button').removeClass('hide');
        }
    });

    var _ModalShade = new BH.Class(BH.Base, {

        _init: function() {
            this.parent._init.call(this);
            this._node = $('<div class="modal-shade hide"></div>');
            
            $('body').append(this._node);

            this.set('clickEvent', new BH.Event());

            this._modals = 0;

            this._behavior();
        },

        _behavior: function() {
            var me = this;
            
            this._node.click(function(e) {
                me.get('clickEvent').fire(e);
            });

            this._node.on('touchstart', function(e) {
                if (me._isVisible) {
                    e.preventDefault();
                }
            });

            this._node.on('touchend', function(e) {
                if (me._isVisible) {
                    me.get('clickEvent').fire();
                }
            });
        },

        show: function() {
            this._modals++;
            this._node.removeClass('hide');
            $('body').addClass('modal-showing');
            this._isVisible = true;
        },

        hide: function() {
            this._modals--;

            if (this._modals === 0) {
                this._node.addClass('hide');
                $('body').removeClass('modal-showing');
                this._isVisible = false;
            }
        }

    });

    if (!BH.ModalShade) {
        BH.ModalShade = new _ModalShade();
    }
});