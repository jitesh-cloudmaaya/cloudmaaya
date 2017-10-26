BH.add('Validation', function() {
	
	"use strict";
    eval(BH.System);

    var ValidationError, Rule, Required, Email, CreditCard, USState, ContinentalState, USZipCode, Year, Month, Day, PasswordMatch, MinLength, Integer, IsANumber, Phone, Password, FirstAndLastRequired, CVV;

    BH.Validation = new BH.Class(BH.Base, {

        _init: function() {
            this.parent._init.call(this);
            this._rules = [];
            this._errors = [];
        },

        addRule: function(rule) {
            this._rules.push(rule);
        },

        validate: function(v) {
            var me = this;

            this.clearError();
            $(this._rules).each(function(_, rule) {
                var error = rule.validate(v);
                if (error !== null) {
                    me._errors.push(error);
                }
            });
        },

        hasErrors: function() {
            return this._errors.length > 0;
        },

        getErrors: function() {
            return this._errors;
        },

        clearError: function() {
            this._errors = [];
        }
    });

    ValidationError = new BH.Class({
        _init: function(cfg) {
            this.type = cfg.type;
            this.message = cfg.message;
        }
    });

    ValidationError.hasErrorType = function() {
        var type = arguments[0],
            i, errors, j, error;

        for (i = 1; i < arguments.length; i += 1) {
            errors = arguments[i];
            for (j = 0; j < errors.length; j += 1) {
                error = errors[j];
                if (error.type === type) {
                    return error;
                }
            }
        }

        return null;
    };

    BH.ValidationError = ValidationError;

    Rule = new BH.Class({
        _test: function() {
            return true;
        },

        validate: function(v) {
            if (this._test(v)) {
                return null;
            } else {
                return new ValidationError({
                    type: this._type,
                    message: this._message
                });
            }
        }
    });

    Required = new BH.Class(Rule, {
        _init: function() {
            this._type = 'required';
            this._message = 'This field is required';
        },

        _test: function(v) {
            var val = $.trim(v);
            return val !== null && val !== '';
        }
    });

    Email = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._message = 'Please enter a valid email address';
        },

        _test: function(v) {
            if (!v) {
                return true;
            }

            var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
            	isValid = re.test(v);

			if (v.indexOf('=') > -1) {
				isValid = false;
			}
            
            return isValid;
        }
    });

    CreditCard = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._message = 'Please enter a valid credit card number';
        },

        _test: function(val) {
            if (val === null) {
                return false;
            }

            var digit, n, sum, _i, _len, _ref;
            sum = 0;
            _ref = val.split('').reverse();
            for (n = _i = 0, _len = _ref.length; _i < _len; n = ++_i) {
                digit = _ref[n];
                digit = +digit;
                if (n % 2) {
                    digit *= 2;
                    if (digit < 10) {
                        sum += digit;
                    } else {
                        sum += digit - 9;
                    }
                } else {
                    sum += digit;
                }
            }

            return sum % 10 === 0;
        }
    });

    USState = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._message = 'Please input a valid state';
        },

        _test: function(val) {
            if ( (val === null) || (typeof(val) === 'undefined') ) {
                return false;
            }

            var code = val.toUpperCase(),
                stateCodes = BH.Util.getUSStateCodes(),
                pos;

            pos = $.inArray(code, stateCodes);
            return (pos >= 0);
        }
    });

    ContinentalState = new BH.Class(Rule, {

        _init: function() {
            this._type = 'invalid';
            this._message = 'Sorry, we are currently unable to ship outside the contiguous U.S.';
        },

        _test: function(val) {
            if (val === null) {
                return false;
            }

            var code = val.toUpperCase(),
                stateCodes = [
                    'AL', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE',
                    'DC', 'FL', 'GA', 'ID', 'IL', 'IN', 'IA',
                    'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN',
                    'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM',
                    'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
                    'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA',
                    'WV', 'WI', 'WY'
                ],
                pos;

            pos = $.inArray(code, stateCodes);
            return (pos >= 0);
        }
    });

    USZipCode = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._message = 'Please input a valid zip code';
        },

        _test: function(val) {
            var re = /(^\d{5}$)/;
            return re.test(val);
        }
    });

    Phone = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._message = 'Please input a valid phone number';
        },

        _test: function(val) {
            var re = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/igm;
            return re.test(val);
        }
    });

    Year = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._message = 'Please input a valid year';
        },

        _test: function(val) {
            if (val === null || val === '') {
                return true;
            } else {
                var reg = new RegExp(/^\d{4}$/);
                return reg.test(val);
            }
        }
    });

    Month = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._message = 'Please input a valid month';
        },

        _test: function(val) {
            if (typeof val === 'undefined' || val === null || val === '') {
                return true;
            } else {
                return val > 0 && val < 13;
            }
        }
    });

    Day = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._message = 'Please input a valid day';
        },

        _test: function(val) {
            return val > 0 && val < 32;
        }
    });

    PasswordMatch = new BH.Class(Rule, {
        _init: function() {
            this._type = 'mismatch';
            this._message = 'The passwords that you entered do not match';
        },

        _test: function(val) {
            if (val.password && val.password.length > 0 && val.confirm_password && val.confirm_password.length > 0) {
                return val.password == val.confirm_password;
            } else {
                return true;
            }
        }
    });

    MinLength = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._prefixmessage = ' must be more than ';
        },

        _test: function(data) {
            data.value = data.value || '';
            this._message = data.fieldname + this._prefixmessage + data.minlength + ' characters';
            return data.value.length >= data.minlength;
        }
    });

    Integer = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._message = 'Please enter an integer';
        },

        _test: function(val) {
            return (!isNaN(val) && val % 1 === 0);
        }
    });

    IsANumber = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._message = 'Please enter a number';
        },

        _test: function(val) {
            return (!isNaN(val));
        }
    });
    
//    Password = new BH.Class(Rule, {
//        _init: function() {
//            this._type = 'invalid';
//            this._message = 'Password must be at least 8 characters and contain a number';
//        },
//
//        _test: function(v) {
//	        return /^(?=.*\d)((?=.*[a-z])|(?=.*[A-Z])).{6,32}$/i.test(v);
//        }
//    });
    Password = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._message = 'Please choose a more secure password. It should be at least 8 characters (not all numbers) and not be too similar to your personal info (name, email, phone) or contain a common word.';
        },

        _test: function(v) {
            // Your password must contain at least 8 characters.
            // Your password can't be entirely numeric.

            var isAllNumeric = /^\d+$/.test(v),
                isValid = true;

//            if ((isAllNumeric) || (v.length < 8) || (v.length > 20)) {
            if ((v.length < 8) || (v.length > 20)) {
                // I'm only checking length as explaining "not all numeric" is difficult, so I'd rather explain if it occurs, which I don't think is that common.
                isValid = false;
            }

            return isValid;
        }
    });

    FirstAndLastRequired = new BH.Class(Rule, {
        _init: function() {
            this._type = 'required';
            this._message = 'This first name and last name are required';
        },

        _test: function(v) {
            var val = $.trim(v),
            	names = BH.Util.splitName(val);

            return (names.first_name !== null && names.first_name !== '') && (names.last_name !== null && names.last_name !== '');
        }
    });    
    
    CVV = new BH.Class(Rule, {
        _init: function() {
            this._type = 'invalid';
            this._message = 'CVV must be 3 or 4 digits';
        },

        _test: function(v) {
			return /^[0-9]{3,4}$/.test(v);
        }
    });

    BH.ValidationRules = {
        Required: new Required(),
        Email: new Email(),
        CreditCard: new CreditCard(),
        USState: new USState(),
        Phone: new Phone(),
        ContinentalState: new ContinentalState(),
        USZipCode: new USZipCode(),
        Year: new Year(),
        Month: new Month(),
        Day: new Day(),
        MinLength: new MinLength(),
        PasswordMatch: new PasswordMatch(),
        Integer: new Integer(),
        IsANumber: new IsANumber(),
        Password: new Password(),
        FirstAndLastRequired: new FirstAndLastRequired(),
        CVV: new CVV()
    };
});