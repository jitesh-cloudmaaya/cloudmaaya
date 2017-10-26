BH.add('Looks', function() {
	
	"use strict";
    eval(BH.System);
    
    // TODO: Refactor this. There is some code that can be shared.
    
    var Look = BH.Class(BH.Widget, {

        _init: function(node, cfg) {
            this.parent._init.call(this, node);
            this._cfg = cfg || {};

            this._left = this._node.find('.bh-id-left');
            this._right = this._node.find('.bh-id-right');

			this.set('collage', new BH.ImageView(this._node.find('.bh-id-collage')));
			this.set('collageBtn', new BH.Button(this._node.find('.bh-id-collage')));
			this.set('descrip', new BH.DescripCommenting(this._node.find('.bh-id-look-descrip')));
			this.set('errorEvent', new BH.Event());
			this.set('heart', new BH.Heart(this._node.find('.bh-id-heart')));
			this.set('heartEvent', new BH.Event());
			this.set('lookNumber', new BH.TextNode(this._node.find('.bh-id-look-number')));
			this.set('name', new BH.TextNode(this._node.find('.bh-id-look-name')));
			this.set('numberOfLooks', new BH.TextNode(this._node.find('.bh-id-number-of-looks')));
//			this.set('openCommentModalEvent', new BH.Event());
            this.set('styledFor', new BH.TextNode(this._node.find('.bh-id-styled-for')));

            this._productList = this._node.find('.bh-id-product-list');
            this._productTpl = this._node.find('.bh-id-product-tpl').removeClass('bh-id-product-tpl hide').remove();
            this.set('products', new BH.List());
        },

        _render: function() {
            this.parent._render.call(this);
            
            this.get('collage').render();
            this.get('collageBtn').render();
            this.get('heart').render();
			this.get('descrip').render();            
        },

        _behavior: function() {
            this.parent._behavior.call(this);
            var me = this;
            
			this.on(this.get('collageBtn').get('clickEvent'), function(event) {
			
				var y = me.get('collage').node().offset().top;
				y -= ($.device.mobile()) ? 100 : 235;

				window.scrollTo(0, y);
			});            
			
			this.on(this.get('descrip').get('errorEvent'), function(data) {
				me.get('errorEvent').fire(data);
			});
			
//			this.on(this.get('descrip').get('openCommentModalEvent'), function(data) {
//				me.get('openCommentModalEvent').fire(data);
//			});
			
			this.on(this.get('heart').get('clickEvent'), function() {

// 				if (me.get('heart').getData()) {
					me.get('heartEvent').fire(me.get('heart').getData());
// 				}
				
				BH.SocialService.addOrUpdateHeart({
					action_value: me.get('heart').getData(),
					look_id: me._data.look_id,
					object: 'look',
					object_id: me._data.look_id
				});
			});
        },
        
        clear: function() {
            this.get('products').clear();
            this._productList.empty();
        },

        doSocialProcessing: function(data) {

			this.get('products').each(function(item, i) {
				
				var product_id = item.getData().product_id;

				if (typeof(data[product_id]) != 'undefined') {
					if (data[product_id].hasOwnProperty('hearted')) {
						if (parseInt(data[product_id].hearted[0].action_value) === 1) {
							item.setToggle(true);
						} else {
							item.setToggle(false);
						}
					} else {
						item.setToggle(false);
					}
				} else {
					item.setToggle(false);
				}
			});
        },

        isFashionista: function(on) {

            if (on) {
                this._left.addClass('hide');
                this._right.removeClass('col-md-6').addClass('col-md-12');
            } else {
                this._left.removeClass('hide');
                this._right.removeClass('col-md-12').addClass('col-md-6');
            }
        },

        setData: function(data) {
			var me = this,
            	products = data.products;
	        
            this._data = data;

			if (data.look_collage) {
	            this.get('collage').setData({
		            'url': data.look_collage
	            });
			}

			if (data.look_descrip) {

				var descripData = {
					'descrip': BH.Util.htmlEntitiesDecode(data.look_descrip),
					'look_id': data.look_id,
					'max_length': ($.device.mobile()) ? 220 : 600
				};

				if (data.comments) {
					descripData.comments = data.comments;
				}
				
				this.get('descrip').setData(descripData);
			}

			if (data.look_name) {
				this.get('name').text(BH.Util.htmlEntitiesDecode(data.look_name));
			}

            if (data.styled_for) {
                this.get('styledFor').text(data.styled_for).show();
            } else {
                this.get('styledFor').hide();
            }

			if (data.look_number) {
				this.get('lookNumber').text(data.look_number);				
			}

			if (data.number_of_looks) {
				this.get('numberOfLooks').text(data.number_of_looks);
			}

			if (data.hearted) {
				this.get('heart').setToggle(parseInt(data.hearted));
			} else {
				this.get('heart').setToggle(false);
			}

            if (data.is_fashionista) {
                this.isFashionista(data.is_fashionista);
            }

			// Products
		    this.clear();

			for (var product_name in products) {

	            var productData = products[product_name],
	            	node = me._productTpl.clone(),
	            	product = new BH.LookProduct(node, this._cfg);

				productData.look_id = data.look_id;
				productData.look_token = data.look_token;
				productData.styling_session_token = data.styling_session_token;

            	product.render();

                productData.is_fashionista = data.is_fashionista;
            	product.setData(productData);

	            me._productList.append(node);

                me.get('products').add(product);

	            me.on(product.get('heartEvent'), function(data) {
		            me.get('heartEvent').fire(data);
	            });
			}
			
			// Social data
			BH.SocialService.getSocialData({
				look_id: me._data.look_id
			}, function(response) {
				me.doSocialProcessing(response);
			}, function(error) {
				BH.log('post ERROR', error);
			});
        }
        
    });    

    BH.Looks = BH.Class(BH.Widget, {

        _init: function(node, cfg) {
            this.parent._init.call(this, node);
            this._cfg = cfg || {};
            
			this.set('commentModal', new BH.CommentModal(this._node.find('.bh-id-comment-modal')));	
			this.set('errorModal', new BH.ErrorModal(this._node.find('.bh-id-error-modal')));
			this.set('heartEvent', new BH.Event());
            this.set('state', new BH.Attr());

            this._lookList = this._node.find('.bh-id-look-list');
            this._lookTpl = this._node.find('.bh-id-look-tpl').removeClass('bh-id-look-tpl hide').remove();
            this.set('looks', new BH.List());
        },

        _render: function() {
            this.parent._render.call(this);
            
            this.get('commentModal').render();
            this.get('errorModal').render();
        },
        
        _behavior: function() {
			this.parent._behavior.call(this);
			var me = this;
        },

        showErrorModal: function(data) {
            this.get('errorModal').setData(data);
			this.get('errorModal').show();
        },
        
        setData: function(data) {
            var me = this;

	        this._data = data;

		    this.clear();

			if (data.looks) {
				
				var looks = data.looks;

				BH.LooksUtil.getCommentsForLooksInSession(function(comments) {
                   me._processLooks(looks, comments);
				}, function(error) {

                    // Commenting this out for now as when this API fails (usually to a lingering CORS issue) it would say the 'invalid session' which even though there is a session. So hiding the error from the user so they can still see their looks.
//					me.showErrorModal({
//						'message': BH.Util.getErrorMessage(error)
//					});

                    me._processLooks(looks, null);
				});
			}
        },

        _processLooks: function(looks, comments) {
            var me = this,
                numberOfLooks = Object.keys(looks).length,
                i = 0;

            for (var look_name in looks) {

                var lookData = looks[look_name],
                    node = this._lookTpl.clone();

                lookData.is_fashionista = this._data.is_fashionista;
                lookData.look_number = i + 1;
                lookData.number_of_looks = numberOfLooks;
                lookData.styling_session_token = this._data.styling_session_token;

                if (comments) {
                    if (typeof(comments[lookData.look_id]) === 'undefined') {
                        lookData.comments = [];
                    } else {
                        lookData.comments = comments[lookData.look_id];
                    }
                } else {
                    lookData.comments = [];
                }

                var look = new Look(node, this._cfg);

                look.render();

                if (i === 0) {
                    if ((this._data.client_first_name) && (this._data.client_last_name)) {
                        lookData.styled_for = 'Styled For ' + this._data.client_first_name + ' ' + this._data.client_last_name;
                    }

                    BH.GoogleAnalytics.trackPageView('SeeLookPage');
                    BH.TrackingService.pageView('look', lookData.look_id, BH.Util.getTokenFromURL());
                }
                look.setData(lookData);

                this._lookList.append(node);

                this.get('looks').add(look);

                this.on(look.get('errorEvent'), function(data) {
                    me.showErrorModal({
                        'message': BH.Util.getErrorMessage(data)
                    });
                });

                this.on(look.get('heartEvent'), function(data) {
                    me.get('heartEvent').fire(data);
                });

                i++;
            }

        },

        clear: function() {
            this.get('looks').clear();
            this._lookList.empty();
        }

    });

});
