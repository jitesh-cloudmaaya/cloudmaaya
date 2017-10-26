BH.add('LooksUtil', function() {

	"use strict";
    eval(BH.System);

    var LooksUtil = BH.Class(BH.Widget, {

        getCommentsForLooksInSession: function(successCb, errorCb) {
	        var me = this;

			BH.SocialService.getCommentsForLooksInASession({
				session_token: BH.Util.getTokenFromURL()
			}, function(response) {

				var comments = [];
				if (response.commented) {
					for (var j = 0; j < response.commented.length; j++) {
						var look_id = response.commented[j].context_id;
						if (typeof(comments[look_id]) === 'undefined') {
							comments[look_id] = [];
						}
						comments[look_id].push(response.commented[j]);
					}
				}

				if (successCb) {
					successCb(comments);
				}

			}, function(error) {
				if (errorCb) {
                    errorCb('session_does_not_exist');
				}
			});
        }

    });

    if (!BH.LooksUtil) {
        BH.LooksUtil = new LooksUtil();
        BH.LooksUtil.render();
    }
});
