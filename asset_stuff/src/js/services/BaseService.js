BH.add('BaseService', function() {
	
	"use strict";
    eval(BH.System);

    var BaseService = BH.Class(BH.Widget, {

		_get: function(data, url, successCb, errorCb, doStringify) {
			var me = this,
				_doStringify = true;
				
			if (typeof(doStringify) !== 'undefined') {
				_doStringify = doStringify;
			}				

			if (_doStringify) {
				data = JSON.stringify(data);
			}

			$.ajax({

				//contentType: "application/json;charset=utf-8",

				// You must use dev.allume.co instead of localhost or this does not work.
				crossDomain: true,
				xhrFields: {
					withCredentials: true
				},
				data: data,
				dataType: 'json',
				type: 'POST',
			    url: url
			    
			}).done(function(response) {
			
				if ((response.code === 'ok') || (response.status === 'success')) {
					
					if (successCb) {
						if (response.data) {
							successCb(response.data);
						} else {
							successCb();
						}
					}	
					
				} else {
					if (errorCb) {
						errorCb(response);
					} else {
						BH.log('ERROR', response);
					}
				}
			
			}).fail(function(error) {
				if (errorCb) {
					errorCb(error);
				} else {
					BH.log('FAIL (BaseService)', url, error);
				}
			});
		}

    });
    
    if (!BH.BaseService) {
        BH.BaseService = new BaseService();
        BH.BaseService.render();
    }
    
});
