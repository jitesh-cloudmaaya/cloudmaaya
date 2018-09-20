BH.add('LookProduct', function() {
	
	"use strict";
    eval(BH.System);

    BH.LookProduct = new BH.Class(BH.Widget, {
	    
        _init: function(node, cfg) {
            this.parent._init.call(this, node);
			this._cfg = cfg || {};

            this._isCollage = false;

			this.set('brand', new BH.TextNode(this._node.find('.bh-id-brand')));
			this.set('heart', new BH.Heart(this._node.find('.bh-id-heart')));
			this.set('heartEvent', new BH.Event());	
			this.set('image', new BH.ImageView(this._node.find('.bh-id-image')));
			this.set('imageViewContainerBtn', new BH.Button(this._node.find('.bh-id-image-view-container')));
			this.set('regularPrice', new BH.TextNode(this._node.find('.bh-id-regular-price')));
			this.set('salePrice', new BH.TextNode(this._node.find('.bh-id-sale-price')));
        },
        
	    _render: function() {
	        this.parent._render.call(this);
	        var me = this;
	        
	        this.get('heart').render();
	        this.get('image').render();
	        this.get('imageViewContainerBtn').render();
	    },
	    
	    _behavior: function() {
			this.parent._behavior.call(this);
			var me = this;
			
			this.on(this.get('heart').get('clickEvent'), function() {

                var thisLookId = me._data.look_id,
                    thisObject = 'product',
                    thisObjectId = me._data.product_id;

                if (me._isCollage) {
                    thisLookId = me._data.object_id;
                    thisObject = 'look';
                    thisObjectId = me._data.object_id;
                }

				BH.SocialService.addOrUpdateHeart({
					action_value: me.get('heart').getData(),
					look_id: thisLookId,
					object: thisObject,
					object_id: thisObjectId
				}, function(success) {
                    me.get('heartEvent').fire(me.get('heart').getData());
				});
			});
	
			this.on(this.get('imageViewContainerBtn').get('clickEvent'), function() {

                if (me._isCollage) {
                    me._goToLooksPage();
                } else {
                    me._goToProductPage();
                }
			});
	    },
		        
        getData: function() {
	        return this._data;
        },

        _goToLooksPage: function() {
            window.location.href = '/looks/' + this.getData().styling_session_token + BH.Util.getModeParam().replace('&', '?');
        },

		// May need to move this to shared space in the future (that is why I have params instead of getting within this method)
		_goToProductPage: function() {

            var fashionistaHash = '';
            if (this._data) {
                if (this._data.is_fashionista) {
                    fashionistaHash = '#fashionista';
                }
            }

			window.location.href = '/product/' + this.getData().product_token + '?lt=' + this.getData().look_token + '&sst=' + this.getData().styling_session_token + BH.Util.getModeParam() + fashionistaHash;
		},

        _getBrand: function(data) {

            if (data.product_brand) {
                return BH.Util.htmlEntitiesDecode(data.product_brand);
            } else if (data.product_retailer) {
                return BH.Util.htmlEntitiesDecode(data.product_retailer);
            } else {
                return '';
            }
        },

        setData: function(data) {
	        var me = this,
                imageUrl = null;
	        
            this._data = data;

            if (data.collage) {
                // Collage

                this._isCollage = true;

                this._node.removeClass('col-md-3').addClass('col-md-6 look');
                this._node.removeClass('col-xs-6').addClass('col-xs-12');

                if (data.collage) {
                    imageUrl = data.collage;
                }

            } else {
                // Product

                this._isCollage = false;

                var _brand = this._getBrand(data);
                if (_brand) {

                    var actual_max_length = BH.Util.getActualMaxLength(_brand, ($.device.mobile()) ? 20 : 30);

                    var brand = BH.Util.htmlEntitiesDecode(_brand.substring(0, actual_max_length));
                    if (_brand.length > actual_max_length) {
                        brand += '&hellip;';
                    }

                    this.get('brand').html(brand);
                } else {
                    this.get('brand').text('');
                }

                if (data.product_price) {
                    this.get('regularPrice').html(BH.Util.moneyFormat(data.product_price));
                } else {
                    this.get('regularPrice').text('');
                }

                if (data.product_sale_price) {
                    this.get('salePrice').text(BH.Util.moneyFormat(data.product_sale_price));
                    this.get('regularPrice').node().addClass('strike');
                } else {
                    this.get('salePrice').node().addClass('hide');
                    this.get('regularPrice').node().removeClass('strike');
                }

                if (data.product_image) {
                    imageUrl = data.product_image;
                }
            }

            if (imageUrl) {
                this.get('image').setData({
                    'url': imageUrl
                });
            }
        },

        setToggle: function(on) {
	        this.get('heart').setToggle(on);
        }
        
    });
});
