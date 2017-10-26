(function(namespace, namespaceName) {

	"use strict";

    var Class = function() {
        var extend = function(subclass, superclass, overrides) {
            var magic = function(fn) {
                return function() {
                    var tmp = this.parent;
                    this.parent = superclass.prototype;
                    var res = fn.apply(this, arguments);
                    this.parent = tmp;
                    return res;
                };
            };

            var k,
                TempClass = function() {
                };

            TempClass.prototype = superclass.prototype;
            subclass.prototype = new TempClass();

            for (k in overrides) {
                subclass.prototype[k] = magic(overrides[k]);
            }

            return superclass.prototype;
        };

        var Class = function() {
            var superclass, methods;

            if (arguments.length === 1) {
                methods = arguments[0];
            } else {
                superclass = arguments[0];
                methods = arguments[1];
            }

            var cls = function() {
                this._init.apply(this, arguments);
            };

            if (superclass) {
                extend(cls, superclass, methods);
            } else {
                cls.prototype = methods;
            }

            return cls;
        };

        return Class;
    }();

    var noStacking = function(fn) {
        var lock = 'stack_lock_' + randomSeed();
        return function() {
            if (this[lock]) {
                return;
            }
            this[lock] = 1;
            var val = fn.apply(this, arguments);
            this[lock] = 0;
            return val;
        };
    };

    var randomSeed = function() {
        return Math.random() * 10000 + '';
    };

    var Base = function() {
        var componentField = 'component_' + randomSeed();

        var cls = Class({
	        
            _init: function() {
                this._destroyEvent = new Event();
                this[componentField] = {};
            },

            set: function(name, o) {
                var field = this[componentField];
                this[componentField][name] = o;

                if (o.onDestroy) {
                    o.onDestroy(function() {
                        delete field[name];
                    });
                }
                return o;
            },

            get: function(name, strict) {
                strict = strict === undefined ? true : strict;
                if (strict && this[componentField][name] === undefined) {
                    throw 'The component: ' + name + ' is undefined.';
                }
                return this[componentField][name];
            },

            has: function(name) {
                return !!this[componentField][name];
            },

            on: function(customEvent, fn) {
                var me = this;

                var removeCb = function() {
                    customEvent.removeListener(fn);
                    me._destroyEvent.removeListener(removeCb);
                };

                customEvent.addListener(fn);
                me.onDestroy(removeCb);
                return removeCb;
            },

            once: function(customEvent, fn) {
                var me = this,
                    cb = function() {
                        fn.apply(me, arguments);
                        removeCb();
                    };

                var removeCb = function() {
                    customEvent.removeListener(cb);
                    me._destroyEvent.removeListener(removeCb);
                };

                customEvent.addListener(cb);
                me.onDestroy(removeCb);
                return removeCb;
            },

            onDestroy: function(fn) {
                this._destroyEvent.addListener(fn);
            },

            // This function is final.  Do not override this function.
            destroy: noStacking(function() {
                for (var k in this[componentField]) {
                    if (this[componentField].hasOwnProperty(k)) {
                        this[componentField][k].destroy();
                    }
                }
                this._destroyEvent.fire();
                this._destroyEvent.destroy();
            })
        });

        return cls;
    }();

    var Attr = new Class({

        _init: function(v) {
            this._value = v;
            this._followers = [];
            this._commanders = [];
            this._changeEvent = new BH.Event();
            this._destroyEvent = new BH.Event();
            this._lock = 0;
        },

        /* Synchronously sets the value of the attribute.  Prevents infinite
         loops by not propogating values to followers if the instance is
         already locked (already propogated the value).  Will not cause
         deadlock, but might cause inconsistent values if two commanders
         change nearly simultaneously, but that case probably doesn't
         occur very often.  Fires the change event after the value has
         been changed and all followers have been notified of the change. */

        set: function(v) {
            if (this._lock === 1) {
                return;
            }
            this._lock = 1;
            var oldV = this._value;
            this._value = v;

            for (var i = 0; i < this._followers.length; i++) {
                this._followers[i].set(v);
            }

            this._changeEvent.fire(v, oldV);
            this._lock = 0;
        },

        get: function() {
            return this._value;
        },

        refresh: function() {
            this.set(this.get());
        },

        // Adding a listener to an attribute listens for when it is changed, or more specifically when it fires a changeEvent.
        addListener: function(fn) {
            this._changeEvent.addListener(fn);
        },

        removeListener: function(fn) {
            this._changeEvent.removeListener(fn);
        },

        on: function(customEvent, fn) {
            customEvent.addListener(fn);
            this.onDestroy(function() {
                customEvent.removeListener(fn);
            });
        },

        // Adds a follower if the follower is not already following this attribute.
        command: function(follower) {
            for (var i = 0; i < this._followers.length; i++) {
                if (follower === this._followers[i]) {
                    return;
                }
            }
            this._followers.push(follower);
            follower._commanders.push(this);
        },

        // Removes a follower from the followers of this attribute, and removes this attribute from the commanders of that follower.
        uncommand: function(follower) {
            removeFromArray(this._followers, follower);
            removeFromArray(follower._commanders, this);
        },

        // Synchronizes two attributes, meaning that when one attribute's value is changed, the other attribute's value is changed too.
        sync: function(other) {
            this.command(other);
            other.command(this);
        },

        onDestroy: function(fn) {
            this._destroyEvent.addListener(fn);
        },

        // Disconnect followers and commanders so that no calls will be made to destroyed objects.
        destroy: function() {
            for (var i = 0; i < this._commanders.length; i++) {
                var commander = this._commanders[i];
                removeFromArray(commander._followers, this);
            }
            for (var j = 0; j < this._followers.length; j++) {
                var follower = this._followers[j];
                removeFromArray(follower._commanders, this);
            }
            this._changeEvent.destroy();
            this._commanders = [];
            this._followers = [];

            this._destroyEvent.fire();
            this._destroyEvent.destroy();
        },

        clear: function() {
            if (this._lock === 1) {
                return;
            }
            this._lock = 1;
            this._value = null;

            for (var i = 0; i < this._followers.length; i++) {
                this._followers[i].clear();
            }

            this._lock = 0;
        }
    });

    var Event = Class({

        _init: function() {
            this._handlers = [];
            this._destroyHandlers = [];
        },

        addListener: function(fn) {
            this._handlers.push(fn);
        },

        removeListener: function(fn) {
            for (var i = 0; i < this._handlers.length; i++) {
                var handler = this._handlers[i];
                if (handler == fn) {
                    this._handlers.splice(i, 1);
                    return;
                }
            }
        },

        fire: function() {
            var handlers = [];

            for (var i = 0; i < this._handlers.length; i++) {
                handlers.push(this._handlers[i]);
            }

            for (var j = 0; j < handlers.length; j++) {
                var handler = handlers[j];
                handler.apply(this, arguments);
            }
        },

        onDestroy: function(fn) {
            this._destroyHandlers.push(fn);
        },

        fireDestroy: function() {
            var handlers = [];

            for (var i = 0; i < this._destroyHandlers.length; i++) {
                handlers.push(this._destroyHandlers[i]);
            }

            for (var j = 0; j < handlers.length; j++) {
                var handler = handlers[j];
                handler.apply(this, arguments);
            }
        },

        destroy: function() {
            this._handlers = [];

            this.fireDestroy();
        }
    });

    var log = function() {
        log.history = log.history || [];
        log.history.push(arguments);

        if (window.console) {
            console.log(Array.prototype.slice.call(arguments));
        }
    };

    var Widget = Class(Base, {
	    
        _init: function(node) {
            Base.prototype._init.call(this);

            this._node = node;
            this._uiLock = false;
            this.set('askForShowEvent', new BH.Event());
        },

        render: function() {
            this._render();
            this._behavior();
        },

        _render: function() {
        },
        
        _behavior: function() {
        },

        _lockUi: function() {
            this._uiLock = true;
        },

        _unlockUi: function() {
            this._uiLock = false;
        },

        _isUiLocked: function() {
            return this._uiLock;
        },

        show: function(cb) {
            this._node.removeClass('hide');
        },

        hide: function(cb) {
            this._node.addClass('hide');
        },

        isVisible: function() {
            return this._node.is(':visible');
        },

        toggleDisplay: function(on) {
            if (typeof on === 'undefined') {
                if (this.isVisible()) {
                    this.hide();
                } else {
                    this.show();
                }
            } else {
                if (on) {
                    this.show();
                } else {
                    this.hide();
                }
            }
        },

        toggleVisibility: function(on) {
            if (typeof on === 'boolean') {
                this._node.toggleClass('invisible', !on);
            } else {
                this._node.toggleClass('invisible');
            }
        },

        node: function() {
            return this._node;
        }
    });
    
	var TextNode = Class(Widget, {
		
        _init: function(node) {
            this.parent._init.call(this, node);
        },

        text: function(text) {
            this._node.text(text);

            return this;
        },

        html: function(html) {
            this._node.html(html);

            return this;
        }
    });
    
    var List = Class(Base, {
	    
        _init: function() {
            Base.prototype._init.call(this);

            var me = this;
            
            this._items = [];
            this._destroyingAll = false;

            this.set('emptyEvt', new Event());
            
            this.onDestroy(function() {
                me.clear();
            });
        },

        add: function(item) {
            var me = this;

            this._items.push(item);

            item.onDestroy(function() {
                me._removeItemFromList(item);
            });
        },

        _removeItemFromList: function(item) {

            if (this._destroyingAll) {
                return;
            }
            
            for (var i = 0; i < this._items.length; i++) {
                var item0 = this._items[i];

                if (item0 === item) {
                    this._items.splice(i, 1);

                    if (this.size() === 0) {
                        this.get('emptyEvt').fire();
                    }

                    return;
                }
            }
        },

        clear: function() {
            this._destroyingAll = true;
            
            for (var i = 0; i < this._items.length; i++) {
                this._items[i].destroy();
            }
            
            this._items = [];
            this._destroyingAll = false;
        },

        each: function(fn) {
            for (var i = 0; i < this._items.length; i++) {
                var item = this._items[i];
                fn(item, i);
            }
        },

        itemAt: function(i) {
            return this._items[i];
        },

        length: function() {
            return this._items.length;
        },

        removeItemAt: function(i) {
            if (i > -1) {
                this._items.splice(i, 1);
            }
        }
    });

	var Image = Class(Widget, {
        _init: function(node) {
            this.parent._init.call(this, node);
        },

        setData: function(url) {
	        this._node.attr('src', url);
        }
    });

    var entity = {
        'Attr': Attr,
        'Base': Base,
        'Class': Class,
        'Event': Event,
        'Image': Image,
        'List': List,
        'log': log,
	    'noStacking': noStacking,
	    'randomSeed': randomSeed,
        'TextNode': TextNode,
        'Widget': Widget,
    };

    (function() {
        var getOpenStr = function(name) {
            return [
                'var ', name, ' = ', namespaceName, '.', name, ';'
            ].join('');
        };

        var openStringAccumulator = [];
        for (var k in entity) {
            if (entity.hasOwnProperty(k)) {
                namespace[k] = entity[k];
                openStringAccumulator.push(getOpenStr(k));
            }
        }

        namespace.System = openStringAccumulator.join('');
    })();

    (function() {
        var added = {};

        namespace.add = function(name, def) {
            if (added[name]) {
                return;
            }

            def();

            added[name] = true;
        };
    })();

})(BH, 'BH');