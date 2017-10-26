BH.add('ProductUtil', function() {
	
	"use strict";
    eval(BH.System);

    var ProductUtil = BH.Class(BH.Widget, {
	    
        // Change image to alternate image for that color (if have it)
        changeImage: function(cfg, imagesByColor, selectedIndex, imageView) {

            var selectedImage = null;

			if (cfg.options[selectedIndex]) {

				var selectedIndexColorName = cfg.options[selectedIndex].name.toLowerCase();
				if (imagesByColor[selectedIndexColorName]) {

					var foundImages = $.grep(imagesByColor[selectedIndexColorName], function(e) { return e.image_size == 'xl'; }),
						useThisImage = foundImages[0].image_url;

					if (BH.Util.isValidUrl(useThisImage)) {
						imageView.setImageUrl(useThisImage);

                        selectedImage = useThisImage;
					}
					
				} else {
					BH.log('No images for ' + selectedIndexColorName);
				}
			}

            return selectedImage;
        },
	    
	    decodeContent: function(content) {
			// Convert "our refined grid jacqua…/li&gt; &lt;li&gt;Imported&lt;/li&gt; &lt;/ul&gt;" to "our refined grid jacqua…% Cotton, 2% Spandex</li> <li>Imported</li> </ul>"
			return $("<div/>").html(content).text();
	    },
	    
	    getAttributeCfg: function(values, defaultLabel) {

			var i = 0,
				attributeOptions = [];
			
			var firstOption = null;
			for (var value in values) {
		        attributeOptions[i] = {
			        'id': value,
			        'name': BH.Util.htmlEntitiesDecode(values[value])
		        };
		        
		        if (i === 0) {
			        firstOption = value;
		        }
		        
		        i++;
			}

			var sortedAttributes = _.sortBy(attributeOptions, 'name');					
			if (defaultLabel.toLowerCase().indexOf('size') > -1) {
				// Size
				sortedAttributes = this._sortSizes(attributeOptions);
			}
			
			var defaultSelected = null;
			if (sortedAttributes.length === 1) {
				defaultSelected = firstOption;
			}
			
/*
			sortedAttributes.unshift({
		        'id': '',
		        'name': defaultLabel
			});		    
*/
			
			var cfg = {
	        	'options': sortedAttributes
	        };
		        
	        if (defaultSelected) {
		        cfg.defaultSelected = defaultSelected;
	        }

		    return cfg;
	    },
	    
	    getProductName: function(data) {
		    var brand = '',
		    	name = '';
		    
		    if (data.product_brand) {
			    brand = data.product_brand;
		    }
		    
		    if (data.product_name) {
			    name = data.product_name;
		    }
		    
		    if (brand.length > 0) {

				if (brand.toLowerCase() === 'asos') {
					brand = 'ASOS';
				}
			    
				name = brand + ' ' + name.replace(brand, '');					    
		    }
		    
			return BH.Util.htmlEntitiesDecode(name);
	    },
	    
	    _sortSizes: function (toBeSorted) {
		    var sorted = [];
		    
			// List of all possible sizes (in order from smallest to largest)
			var allPossibleSizes = [
				'2P', '2', '4P', '4', '5', '5.5', '6P', '6', '6.5', '7', '7.5', '8P', '8', '8.5', '9', '9.5', '10P', '10', '11', '12P', '12', '13', '14', '16',

				'5 M', '5M', '5.5 M', '5.5M', '6 M', '6M', '6.5 M', '6.5M', '7 M', '7M', '7.5 M', '7.5M', '8 M', '8M', '8.5 M', '8.5M', '9 M', '9M', '9.5 M', '9.5M', '10 M', '10M', '10.5 M', '11 M', '11M', '12 M', '13 M', 

				'XX-Small', 'X-Small', 'Small', 'Medium', 'Large', 'X-Large P', 'X-Large',

				'Regular XS', 'Regular S', 'Regular M', 'Regular L', 'Regular XL', 'Regular XXL',
				
				'petite x 00', 'regular x 00', 'petite x 0', 'regular x 0', 'petite x 2', 'regular x 2', 'petite x 4', 'regular x 4', 'petite x 6', 'regular x 6', 'petite x 8', 'regular x 8', 'petite x 10', 'regular x 10', 'petite x 12', 'regular x 12', 'petite x 14', 'regular x 14', 'petite x 16', 'regular x 16', 'regular x 18',
				
				'6 X M', '6.5 X M', '7 X M', '7.5 X M', '8 X M', '8.5 X M', '9 X M', '9.5 X M', '10 X M',
				
				'XS', 'S', 'M', 'L', 'XL',
				
				'US 0', 'US 2', 'US 4', 'US 6', 'US 8', 'US 10', 'US 12', 'US 14', 'US 16',
				
				'5.5 x Medium', 
				'6 x Medium', '6 x Wide', 
				'6.5 x Medium', '6.5 x Wide', 
				'7 x Narrow', '7 x Medium', '7 x Wide', '7 x Extra Wide', 
				'7.5 x Narrow', '7.5 x Medium', '7.5 x Wide', '7.5 x Extra Wide', 
				'8 x Narrow', '8 x Medium', '8 x Wide', '8 x Extra Wide', 
				'8.5 x Narrow', '8.5 x Medium', '8.5 x Wide', '8.5 x Extra Wide', 
				'9 x Narrow', '9 x Medium', '9 x Wide', '9 x Extra Wide', 
				'9.5 x Medium', '9.5 x Wide', 
				'10 x Narrow', '10 x Medium', '10 x Wide', '10 x Extra Wide', 
				'11 x Medium', '11 x Wide', '11 x Extra Wide'
			];
			// Least number sizes (e.g. 23, 32) out of this list as they will be sorted already

			_.each(_.sortBy(toBeSorted, 'name'), function(item, idx) {

				if (allPossibleSizes.indexOf(item.name) > -1) {
					
					sorted.push({
						'id': item.id,
						'name': item.name,
						'sequence': allPossibleSizes.indexOf(item.name)
					});
				
				} else {
					
					// This handles number sizes that fall through (e.g. 23, 32)
					sorted.push({
						'id': item.id,
						'name': item.name,
						'sequence': allPossibleSizes.indexOf(item.name)
					});
					
				}
				
			});
			
			return _.sortBy(sorted, 'sequence');		    
	    },
	    
	    getImagesByColor: function(alternateImages, groupByPropertyName) {
		    
			var groupedByColor = _.groupBy(alternateImages, groupByPropertyName);
			
			// Lowercase keys (color names) to avoid issues when using e.g. "Light beige" vs "Light beige"
			var key = '',
				keys = Object.keys(groupedByColor),
				n = keys.length,
				groupedByColorLowercase = {};
				
			while (n--) {
				key = keys[n];
				groupedByColorLowercase[key.toLowerCase()] = groupedByColor[key];
			}

		    return groupedByColorLowercase;
	    },
	    
        shouldHideOption: function(options) {
	        
			var hideOption = false;
			if (options.length === 1) {
// 				if (options[0] === '') {
					hideOption = true;
// 				}
			}
	        
			return hideOption;
        }
	        
    });

    if (!BH.ProductUtil) {
        BH.ProductUtil = new ProductUtil();
        BH.ProductUtil.render();
    }
});
