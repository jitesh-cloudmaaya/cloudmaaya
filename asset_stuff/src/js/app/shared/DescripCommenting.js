BH.add('DescripCommenting', function() {
	
	"use strict";
    eval(BH.System);

	// This widget uses: html/templates/partials/looks/descrip_commenting.html, css/looks/descrip_commenting.css

    var Comment = BH.Class(BH.Widget, {

        _init: function(node, cfg) {
            this.parent._init.call(this, node);
            this._cfg = cfg || {};
            
            this.set('avatar', new BH.TextNode(this._node.find('.bh-id-client-avatar')));
            this.set('comment', new BH.TextNode(this._node.find('.bh-id-client-comment')));
        },

/*
        _render: function() {
            this.parent._render.call(this);
        },

        _behavior: function() {
            this.parent._behavior.call(this);
            var me = this;
        },
*/
        
        setData: function(data) {
	        
			if (data.user_name) {
				this.get('avatar').text(BH.Util.getInitials(data.user_name));
			} else {
				this.get('avatar').text('');
			}
	        
	        if (data.action_value) {
				this.get('comment').text(data.action_value);		        
	        }

        }
    });

    BH.DescripCommenting = new BH.Class(BH.Widget, {
	    
        _init: function(node, cfg) {
            this.parent._init.call(this, node);
			this._cfg = cfg || {};
			
// 			this._is_open = false;
			
			this._allumeAvatar = this._node.find('.bh-id-allume-avatar');
			
            this.set('comment', new BH.TextAreaInput(this._node.find('.bh-id-comment'), {
                useCharCountdown: false,
                maxlength: 400
            }));
			
			this.set('beginning', new BH.TextNode(this._node.find('.bh-id-beginning')));
			this.set('commenting', new BH.Widget(this._node.find('.bh-id-commenting')));
			this.set('end', new BH.TextNode(this._node.find('.bh-id-end')));
			this.set('errorEvent', new BH.Event());
			this.set('lessBtn', new BH.Button(this._node.find('.bh-id-less')));
			this.set('moreBtn', new BH.Button(this._node.find('.bh-id-more')));
			this.set('openCommentModalEvent', new BH.Event());
			this.set('submitBtn', new BH.Button(this._node.find('.bh-id-submit')));

            this._commentList = this._node.find('.bh-id-comment-list');
            this._commentTpl = this._node.find('.bh-id-comment-tpl').removeClass('bh-id-comment-tpl hide').remove();
            this.set('comments', new BH.List());
        },

        _render: function() {
            this.parent._render.call(this);
            
			this.get('beginning').render();
			this.get('comment').render();
			this.get('end').render();
			this.get('lessBtn').render();
			this.get('moreBtn').render();
			this.get('submitBtn').render();
        },

        _behavior: function() {
            var me = this;

/*
			this.on(this.get('comment').get('keyupEvent'), function() {
				
				if (me.get('comment').getData().length > 0) {
					me.get('submitBtn').enable();
				} else {
					me.get('submitBtn').disable();
				}
			});
*/

			this.on(this.get('lessBtn').get('clickEvent'), function() {

//				if ($.device.mobile()) {
					me._allumeAvatar.removeClass('visible-xs-inline-block');
					me.get('commenting').hide();
					me.get('lessBtn').hide();
					me._commentList.addClass('hide');
//				}

				me.get('moreBtn').show();
				me.get('end').hide();

// 				me._is_open = false;
			});

			this.on(this.get('moreBtn').get('clickEvent'), function() {
				
//				if ($.device.mobile()) {
					me._allumeAvatar.addClass('visible-xs-inline-block');
					me.get('commenting').show();
					me.get('lessBtn').show();
					me.get('moreBtn').hide();
					me.get('end').show();
					me._commentList.removeClass('hide');
//				} else {
//					me.get('openCommentModalEvent').fire(me._data);
//				}

// 				me._is_open = true;
			});
			
			this.on(this.get('submitBtn').get('clickEvent'), function() {

				if (me.get('comment').getData().length > 0) {

					me.get('submitBtn').toggleProcessing(true);
					me.get('comment').disable();
				
					BH.SocialService.addOrUpdateComment({
						action_value: me.get('comment').getData(),
						look_id: me._data.look_id,
						object: 'look',
						object_id: me._data.look_id
					}, function(response) {

						me._postCommentProcessing();

					}, function(error) {
						me.get('errorEvent').fire(error);
						me.get('comment').enable();
						me.get('submitBtn').toggleProcessing(false);
					});
				}
			});
        },

        clear: function() {
            this.get('comments').clear();
            this._commentList.empty();
        },

		_postCommentProcessing: function() {
			var me = this;

			BH.LooksUtil.getCommentsForLooksInSession(function(comments) {

				if (comments[me._data.look_id]) {
					me.refreshComments(comments[me._data.look_id]);
				}

				me.get('comment').clear();
				me.get('comment').enable();
				me.get('submitBtn').toggleProcessing(false);
			}, function(error) {
				me.get('errorEvent').fire(error);
				me.get('comment').enable();
				me.get('submitBtn').toggleProcessing(false);
			});
		},

        refreshComments: function(comments) {
	        
		    this.clear();

			for (var i = 0; i < comments.length; i++) {
				
				var commentData = comments[i],
					node = this._commentTpl.clone(),
					comment = new Comment(node, this._cfg);
					
            	comment.render();
            	comment.setData(commentData);
            	
            	this._commentList.append(node);
            	this.get('comments').add(comment);
			}
        },
        
        setData: function(data) {
	        
	        this._data = data;

	        if (data.descrip) {
				if (data.max_length) {
					
					// css text-overflow: ellipsis?
					if (data.descrip.length > data.max_length) {
						
						var actual_max_length = BH.Util.getActualMaxLength(data.descrip, data.max_length),
							beginning = data.descrip.substring(0, actual_max_length),
							end = data.descrip.substring(actual_max_length);

						this.get('beginning').text(beginning);
						this.get('end').text(end);
                        this.get('moreBtn').node().text('.. MORE');
					} else {
						this.get('beginning').text(data.descrip);
                        this.get('moreBtn').node().text('... COMMENT');
					}
					
				} else {
					this.get('beginning').text(data.descrip);
				}
	        }
	        
	        this.refreshComments(data.comments);
        }
        
    });
});