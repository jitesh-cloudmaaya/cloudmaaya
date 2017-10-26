BH.add('LooksHeader', function() {

	"use strict";
    eval(BH.System);

	// This widget used html/templates/partials/header_looks.html

    BH.LooksHeader = new BH.Class(BH.Widget, {

        _init: function(node, cfg) {
            this.parent._init.call(this, node);
			this._cfg = cfg || {};

			this._count = 0;
			this._data = {};
			this._stylingSessionToken = '';

			this._heart = this._node.find('.bh-id-heart-container img');
			this._heartModal = $('body').find('.bh-id-heart-modal');

			this.set('heartBtn', new BH.Button(this._node.find('.bh-id-heart-container')));
            this.set('heartModal', new BH.Modal({
                closeButtons: this._heartModal.find('.bh-id-close'),
                dismissable: true,
                node: this._heartModal
            }));

			this.set('bagBtn', new BH.Button(this._node.find('.bh-id-bag')));
			this.set('cartCount', new BH.TextNode(this._node.find('.bh-id-bag-count')));
			this.set('setCartCountEvent', new BH.Event());

            this.set('logoBtn', new BH.Button(this._node.find('.bh-id-logo-link')));

            this.set('clientName', new BH.TextNode(this._node.find('.bh-id-client-name')));
            this.set('loginBtn', new BH.Button(this._node.find('.bh-id-login')));
            this.set('logoutBtn', new BH.Button(this._node.find('.bh-id-logout')));

            this.set('signedIn', new BH.Widget(this._node.find('.bh-id-signed-in')));
            this.set('signedOut', new BH.Widget(this._node.find('.bh-id-signed-out')));
        },

        _render: function() {
            this.parent._render.call(this);

            this.get('bagBtn').render();
            this.get('heartBtn').render();
            this.get('loginBtn').render();
            this.get('logoBtn').render();
            this.get('logoutBtn').render();
            this.get('signedIn').render();
            this.get('signedOut').render();

            this._setup();
        },

        _behavior: function() {
            var me = this;

            this._heart.on('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function() {
				me._heart.removeClass('tada');
            });

            this.on(this.get('logoBtn').get('clickEvent'), function(e) {
                e.preventDefault();
                me._goToLooksPage();
            });

            this.on(this.get('bagBtn').get('clickEvent'), function() {
				if (me._count > 0) {
					me._goToCartPage();
				}
			});

            this.on(this.get('heartBtn').get('clickEvent'), function() {
				me._goToHeartsPage();
			});

            this.on(this.get('loginBtn').get('clickEvent'), function(e) {
                e.preventDefault();
                me.login();
            });

            this.on(this.get('logoutBtn').get('clickEvent'), function(e) {
                e.preventDefault();
                me.logout();
            });
        },

        calculateCartCount: function(items) {

			var cartCount = 0;
			_.each(items, function(item, idx) {
				cartCount += item.quantity;
			});

			this.setCartCount(cartCount);
        },

		getCart: function () {
			return this._data;
		},

        _goToCartPage: function() {
			window.location.href = '/cart/?sst=' + this._stylingSessionToken + BH.Util.getModeParam();
        },

        _goToHeartsPage: function() {
			window.location.href = '/hearts/?sst=' + this._stylingSessionToken + BH.Util.getModeParam();
        },

        _goToLooksPage: function() {
			window.location.href = '/looks/' + this._stylingSessionToken + BH.Util.getModeParam().replace('&', '?');
        },

		loadCart: function() {
			var me = this;

	        BH.EcommerceService.getCart(
	        	function(data) {

		        	if (data) {
			        	me._data = data;

						me.calculateCartCount(data.items);
		        	}
	        	}
	        );

		},

        login: function() {

            BH.log('sign in');

            // TODO: Open SignInModal

        },

        logout: function() {

            BH.log('sign out');

//            BH.EcommerceService.logout(
//                function(success) {
//
//                    BH.log('logout', success);
//
//
//
//
//                    // TODO: Delete allume-user-name cookie (if I user it)
//
//                },
//                function(error) {
//
//                    BH.log('logout', error);
//
//                }
//            );

        },

		refresh: function() {
	        var me = this;

			var now = (new Date()).getTime();

			// Use global variable here, look for in loadCart in LooksHeader, if works after a while then expand user to other APIs
			var hasIdCheck = setInterval(function() {

				var later = (new Date()).getTime(),
					diff = later - now;

				if ((BH.Globals.haveVisitorId) || (diff > 4000)) {
					clearInterval(hasIdCheck);
					me.loadCart();
				}

			}, 200);
		},

		setCart: function(data) {
			this._data = data;
		},

        setCartCount: function(cartCount) {
	        this._count = cartCount;
	        this.get('cartCount').text(cartCount);
	        this.get('setCartCountEvent').fire(this._data);
        },

		setStylingSessionToken: function(token) {
			this._stylingSessionToken = token.replace('?m=1', '');
		},

        _setup: function() {
            var me = this,
                clientName = '',
                userCookie = Cookies.get('allume-user-name') || '';




            // TODO: Move this header login/logout to it's own widget so can share on LLP and HP -- use SignInModal.js ???





            // TODO: is_logged_in always returning false on purpose
            BH.EcommerceService.isLoggedIn(function(response) {

                BH.log('isLoggedIn OK', response);

				if (response) {
					// Signed in

                    BH.log('Signed IN');

				} else {
					// Signed out

                    BH.log('Signed OUT');

				}

            }, function(error) {

                BH.log('isLoggedIn ERROR', error);

            });







            // Is the client signed in?
            if (userCookie !== '') {
                // Signed In

                this.get('clientName').text(userCookie);

                this.get('signedOut').hide();
                this.get('signedIn').show();

            } else {
                // Signed Out

                this.get('signedIn').hide();
                this.get('signedOut').show();

            }

//            BH.EcommerceService.forgotPassword({
//                'user_login': 'aaron+test1@allume.co'
//            }, function(response) {
//
//                BH.log('login', response);
//
//            }, function(error) {
//
//                BH.log('ERROR', error);
//
//            });

//            BH.EcommerceService.login({
//                log: 'aaron+test1@allume.co',
//                pwd: 'testing1'
//            }, function(response) {
//
//                BH.log('login', response);
//                // TODO: Need client name
//                if (response) {
//                    clientName = response;
//                }
//
//                me.get('clientName').text(clientName);
//
//                // Do we need this?
//                // Should I save more than the name?
//                Cookies.set('allume-user-name', clientName, { domain: '.allume.co', expires: 90, path: '/', secure: true });
//
////                Cookies.get(cookieName)
//
//            }, function(error) {
//
//                BH.log('ERROR', error);
//
//            });

        },

        triggerEffect: function() {
	        this._heart.addClass('tada');

	  		// Only show the heart-modal the first time
			if (Cookies.get('allume-first-heart') && (Cookies.get('allume-first-heart') === 'shown')) {
				// Seen it
			} else {
		        Cookies.set('allume-first-heart', 'shown', { domain: '.allume.co', expires: 90, path: '/', secure: true });
		  		this.get('heartModal').show();
	  		}
        }

    });
});