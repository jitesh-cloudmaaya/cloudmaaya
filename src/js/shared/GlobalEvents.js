BH.add('GlobalEvents', function() {
	
	"use strict";
    eval(BH.System);

    var GlobalEvents = BH.Class(BH.Widget, {

		_init: function(cfg) {
			var me = this;
			cfg = cfg || {};
			this.parent._init.call(this);
		
			_.each(cfg.events, function(evtName) {
				me.set(evtName, new BH.Event());
			});
		}
		
    });

    if (!BH.GlobalEvents) {
        BH.GlobalEvents = new GlobalEvents({
	        'events': ['incompleteQuizInOtherDeviceEvent', 'setVisitorIdEvent']
        });
    }
});
