/**
* @description search_page namespace object, conatining the functionality and templates for the search page
*/
var search_page = {
  /** 
  * @description cache of styling session
  */
  session_id: '',
  /**
  * @description variable to cache the allume sizing API call
  */
  cached_sizes: null,
  /**
  * @description init function applying the functionality to the page elements
  */
  init: function(){
    /* cache the session id */
    search_page.session_id = $('body').data('stylesession');
    /* get allume sizes and cache for use in searches */
    $.ajax({
      contentType: 'application/json',
      crossDomain: true,
      type: 'POST',
      url: 'https://styling-service-' + local_environment + '.allume.co/get_allume_sizes/',
      xhrFields: {
        withCredentials: true
      },
      success: function(response){
        var obj = JSON.parse(response);
        console.log(obj);
        if(obj.status == 'success' && obj.data != undefined){
          search_page.cached_sizes = obj.data;
        }
      },
      error: function(response){
        console.log(response)
      }
    });
    /* search functionality */
    $('#search-btn').click(function(e){
      e.preventDefault();
      search_page.performSearch(1, false, null);
    });
    $("#search-field").val('').keyup(function(event) {
      if (event.keyCode === 13) {
        search_page.performSearch(1, false, null);
      }
    });

    $('#sort-dd').val(' ').selectize({ create: false, sortField: 'text'}).change(function(e){
      search_page.performSearch(1, false, null);
    });

    $('#client-defaults').html(
      '<div class="client-settings"><h5>Client preferences:</h5>' +
      '<span><em>colors:</em>' + client_360.colors + '</span>' +
      '<span><em>styles to avoid:</em>' + client_360.avoid + '</span></div>'
    );
    $('#search-categories').val('').selectize({ 
      create: false
    }).change(function(){
      var dd = $(this);
      var val = dd.val();
      var def_div = $('#client-defaults');
      var header = '<h5>Client preferences and sizes for <strong>' + val + '</strong>:</h5>';
      var general = '<span><em>colors:</em>' + client_360.colors + '</span>' +
        '<span><em>styles to avoid:</em>' + client_360.avoid + '</span>';
      if(utils.category_settings == null){
        if(["Dresses", "Jackets"].indexOf(val) > -1){
          def_div.html(
            '<div class="client-settings">' + header +
            '<span><em>spend:</em>' + client_360.categories[val].spend + '</span>' +
            '<span><em>style:</em>' + client_360.categories[val].style + '</span>' +
            general + '</div>'
          );        
        }else if(["Jeans", "Shoes", "Tops"].indexOf(val) > -1){
          def_div.html(
            '<div class="client-settings">' + header +
            '<span><em>spend:</em>' + client_360.categories[val].spend + '</span>' +
            '<span><em>style:</em>' + client_360.categories[val].style + '</span>' +
            '<span><em>size:</em>' + client_360.categories[val].size + '</span>' +
            general + '</div>'
          );  
        }else if(val == "Bottoms"){
          def_div.html(
            '<div class="client-settings">' + header +
            '<span><em>spend:</em>' + client_360.categories[val].spend + '</span>' +
            '<span><em>size:</em>' + client_360.categories[val].size + '</span>' +
            general + '</div>'
          );          
        }else{
          def_div.html(
            '<div class="client-settings"><h5>Client preferences:</h5>' +
            '<span><em>colors:</em>' + client_360.colors + '</span>' +
            '<span><em>styles to avoid:</em>' + client_360.avoid + '</span></div>'
          );
        }
      }else{
        utils.setHelp(val);    
      }
    });
    /* facets functionality */
    $('#facets').on('click', 'a.facet-group', function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('on')){
        link.removeClass('on').find('span').html('+');
      }else{
        link.addClass('on').find('span').html('-');
      }
      link.next('div').slideToggle();
    }).on('change','input.facet-box',function(e){
      var box = $(this);
      var facet_links = $('#search-form-selections');
      search_page.performSearch(1, false, null);
    }).on('click', 'a.size-facet-sub', function(e){
      e.preventDefault();
      var link = $(this);
      var div = link.next('div');
      if(link.hasClass('open')){
        link.removeClass('open').find('span').html('+');
        div.slideUp();
      }else{
        link.addClass('open').find('span').html('-');
        div.slideDown();
      }
    }).on('click', 'a.size-group-toggle', function(e){
      e.preventDefault();
      var link = $(this);
      var div = $(link.attr('href'));
      if(link.hasClass('open')){
        link.removeClass('open').find('span').html('+');
        div.slideUp();
      }else{
        link.addClass('open').find('span').html('-');
        div.slideDown();
      }
    }).on('change','input.allume-size',function(e){
      var box = $(this);
      var div = $(box.data('groupdiv'));
      if(box.prop('checked')){
        div.find('input').prop('checked', true);
      }else{
        div.find('input').prop('checked', false);
      }
      search_page.performSearch(1, false, null);
    }).on('change','input.size-member',function(e){
      var box = $(this);
      var div = box.closest('div.sizegroup-list');
      var checked = div.find('input:checked');
      if(checked.length == 0){
        div.prev('label').find('input').prop('checked',false);
      }
      if(box.prop('checked')){
        div.prev('label').find('input').prop('checked',true);
      }
      search_page.performSearch(1, false. null);
    })
    $('#search-form-selections').on('click', 'a', function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('remove-search')){
        $('#search-field').val('');
      }else if(link.hasClass('remove-category')){
        $('#search-categories')[0].selectize.setValue('',true);
      }else if(link.hasClass('size')){
        var div = $(link.data('sizegroup'));
        div.find('input').prop('checked', false);
        div.prev('label').find('input').prop('checked', false);
      }else{
        var facets = $('#facets');
        var facet = link.data('facet');
        var group = link.data('qparam');
        var group_div = facets.find('div[data-qparam="' + group + '"]');
        var facet_link = group_div.find('input[value="' + facet + '"]');
        facet_link.prop('checked', false);
      }
      search_page.performSearch(1, false. null);
    });
    $('#facet-show-faves').prop('checked', false).click(function(e){
      search_page.performSearch(1, false, null);
    });
    /* pager functionality */
    $('#pager').on('click','a.page',function(e){
      e.preventDefault();
      var link = $(this);
      search_page.performSearch(parseInt(link.data('page')), false, null);
      $('html,body').animate({ scrollTop: 0 }, 300);
    }); 
    /* results functionality */
    $('#results').on('click','a.favorite',function(e){
      e.preventDefault();
      var link = $(this);
      rack_builder.addFavorite(link);
    }).on('click','a.add-to-rack',function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('selected') == false){
        rack_builder.addToRack(link, 'search', false);
      }
    }).on('click','a.item-detail',function(e){
      e.preventDefault();
      var link = $(this);
      rack_builder.inspectItem(link, 'search');
    });   
    /* clear search filters */
    $('#clear-search-filters').click(function(e){
      e.preventDefault()
      var link = $(this);
      $.each($('#facets input:checked'), function(idx){
        $(this).prop('checked', false);
      });
    });
    /* ANNA store list funcs */
    $('#view-stores').click(function(e){
      e.preventDefault();
      $('#anna-store-list').fadeIn();
    });
    $('#close-store-list').click(function(e){
      e.preventDefault();
      $('#anna-store-list').fadeOut();
    });
    /* check last search cookie and load if exists */
    var search_cookie = utils.readCookie('lastShoppingToolSearch' + search_page.session_id);
    if(search_cookie != null){
      var last_search = utils.parseQuery(search_cookie);
      var search_box = $('#search-field');
      var category = $('#search-categories');
      var sanitized_primary ='';
      if(last_search.primary_category != undefined){
        sanitized_primary = last_search.primary_category;
      }

      category[0].selectize.setValue(sanitized_primary, false);
      search_box.val(last_search.text);
      if(last_search.favs != undefined){
        $('#facet-show-faves').prop('checked', true);
      }
      search_page.performSearch(last_search.page, true, last_search);
    }
  },
  /**
  * @description processing and template for facets
  * @param {object} facets - the facets object
  * @param {string} category - category string
  */
  facetTemplate: function(facets, category){
    var markup = [];
    var cs = $('#search-field').data();
    if(facets != undefined){
      var social_facets = [];
      var group_markup = {names: [], markup: {}}
      /* build initial list of facet buckets */
      var display_order = ['_filter_price_range','_filter_brand',
                           '_filter_merchant_name','_filter_color','_filter_material'];

      markup.push(search_page.sizeFacetTemplate(category));
      for(var i = 0, l = display_order.length; i<l; i++){
        var bucket = display_order[i];
        var facet_list = facets[bucket];
        if(facet_list){
          if(['_filter_is_best_seller', '_filter_is_trending'].indexOf(bucket) == -1){
            var display_name = bucket.replace('_filter_', '');
            var pretty_name = display_name;
            if(display_name == 'merchant_name'){pretty_name = 'store'}
            group_markup.names.push(display_name);
            group_markup.markup[display_name] = [];
            group_markup.markup[display_name].push(
              '<a href="#" class="facet-group"><span>+</span>' + 
              utils.capitalizeEveryWord(pretty_name.replace(/_/g, ' ')) + 
              '</a><div class="facet-list" data-qparam="' + display_name + '">'
            );
            if(display_name == 'price_range'){
              facet_list[display_name].buckets.sort(function(a,b){
                if(a.from == undefined){a.from == 0}
                if(b.from == undefined){b.from == 0}
                if(a.from > b.from){ return 1}
                if(a.from < b.from){ return -1}
                return 0;
              })
            }else{
              facet_list[display_name].buckets.sort(function(a,b){
                if(a.key.toLowerCase() > b.key.toLowerCase()){ return 1}
                if(a.key.toLowerCase() < b.key.toLowerCase()){ return -1}
                return 0;
              })
            }
            for(var j = 0, num = facet_list[display_name].buckets.length; j<num; j++){
              var facet = facet_list[display_name].buckets[j];
              var checked = '';
              if((pretty_name == 'size')&&(cs.clientsettings == true)){
                var sizes = cs.clientsize.split('|');
                if(sizes.indexOf(facet.key) > -1){
                  checked = "checked";
                }
              }
              /* for facets with subcategories add breakers and clearers */
              if(facet.key == 'special-breaker'){
                group_markup.markup[display_name].push('<span class="facet-breaker"></span>')
              }else if(facet.key == 'facet-clear'){
                group_markup.markup[display_name].push('<span class="facet-clear"></span>')
              }else{
                if((facet.key != '')&&(facet.key != 'sort')){
                  group_markup.markup[display_name].push(
                    '<label class="facet">' +
                    '<input class="facet-box" type="checkbox" value="' + 
                    facet.key + '" ' + checked + ' data-facetgroup="' + 
                    display_name + '"/><span>' + '<i class="fa fa-circle-thin"></i>' +
                    '<i class="fa fa-check-circle"></i>' +
                    '</span><em class="number">' + 
                    numeral(facet.doc_count).format('0,0') +
                    '</em><em class="key">' + facet.key + '</em></label>'
                  );
                }
              }
            }
            group_markup.markup[display_name].push('</div>');
          }else{
            social_facets.push(facet_list);
          }
        }
      }
      if(social_facets.length > 0){
        group_markup.names.push('social');
        group_markup.markup['social'] = [];
        group_markup.markup['social'].push(
          '<a href="#" class="facet-group"><span>+</span>Social' +
          '</a><div class="facet-list" data-qparam="social">'
        );
        for(var i = 0, l = social_facets.length; i<l; i++){
          var facet = social_facets[i];
          var keys = Object.keys(facet);
          for(j = 0, k = keys.length; j<k; j++){
            var key = keys[j];
            if(key != 'doc_count'){
              group_markup.markup['social'].push(
                '<label class="facet">' +
                '<input class="facet-box special" type="checkbox" value="' + 
                key + '" data-facetgroup="' + key + '"/><span>' +
                '<i class="fa fa-circle-thin"></i>' +
                '<i class="fa fa-check-circle"></i>' +
                '</span><em class="number">' + 
                numeral(facet['doc_count']).format('0,0') +
                '</em><em class="key">' + key.replace(/_/g, ' ').replace('is ', '') + '</em></label>'
              );
            }
          }
        }
        group_markup.markup['social'].push('</div>');
      }
      for(var i = 0, l = group_markup.names.length; i<l; i++){
        var group_name = group_markup.names[i];
        markup.push(group_markup.markup[group_name].join(''));
      }
      $('#facets').html(markup.join(''));
      $('#search-field').data('clientsettings', false);
    }    
  },
  /**
  * @description from facet values return array of "allume" sizes
  * @param {array} sizes - list of sizes to process
  * @param {string} category - search category
  * @returns {array} Array of allume sizes
  */
  getAllumSizes: function(sizes, category){
    var size_block = facet_sizing;
    if(search_page.cached_sizes != null){
      size_block = search_page.cached_sizes.mapped;
    }
    /* get all the various sizes for each type */
    var clothing_sizes = size_block.regular_sizes.concat(size_block.petite_sizes.concat(size_block.tall_sizes));
    var shoe_sizes = size_block.regular_shoes.concat(size_block.narrow_shoes.concat(size_block.wide_shoes));
    var allume_sizes = [];
    /**
    * @description private helper function to generate array of allume sizes
    * @param {array} all_sizes - array of sizes to process
    * @param {object} member_hash - member hash to get member lists  
    * @param {array} sizes_to_check - array of sizes to match with allume sizes      
    * @returns {array} - array of allume sizes
    */
    function sizeMatching(all_sizes, member_hash, sizes_to_check){
      var matched_size = [];
      for(var i = 0, l = all_sizes.length; i<l; i++){
        var size_grouping = all_sizes[i];
        var subset_sizes = member_hash[size_grouping].sizes;
        var matched = 0;
        for(var ix = 0, lx = sizes_to_check.length; ix<lx; ix++){
          if(size_grouping == String(sizes_to_check[ix])){
            matched = 1;
            matched_size.push(size_grouping);
          }
        }
        if(matched == 0){
          for(var ix = 0, lx = subset_sizes.length; ix<lx; ix++){
            var size = subset_sizes[ix];
            var sub_match = 0;
            for(var j = 0, n = sizes_to_check.length; j<n; j++){
              if(size == String(sizes_to_check[j])){
                sub_match = 1;
                matched_size.push(size_grouping);
              }
            }
          }
        }
      }
      /* unique the matched sizes */
      return [...new Set(matched_size)];
    }
    if (category == '') {
      var all_sizes = sizeMatching(shoe_sizes, size_block.shoe_members, sizes).concat(
        sizeMatching(shoe_sizes, size_block.shoe_members, sizes).concat(
          sizeMatching(size_block.one_size, size_block.clothing_members, sizes)
        )
      );
      return all_sizes;
    } else if (category == 'Shoes') {
      return sizeMatching(shoe_sizes, size_block.shoe_members, sizes);
    } else if (["Shoes","Accessories","Other","Beauty","Unsure"].indexOf(category) == -1) {
      return sizeMatching(clothing_sizes, size_block.clothing_members, sizes);
    } else {
      return sizeMatching(size_block.one_size, size_block.clothing_members, sizes);
    }
  },
  /**
  * @description item template for results and rack
  * @param {object} details - item details JSON
  * @param {string} view - which display 
  * @param {array} hits - other versions of the product 
  * @returns {string} HTML
  */   
  itemTemplate: function(details, view, hits){
    var products = hits.concat({_source: details});
    var colors_hash = rack_builder.createColorHash(products);
    var desc = details.long_product_description == '' ? details.short_product_description : details.long_product_description ;
    var price_display = '<span class="price">' + numeral(details.current_price).format('$0,0.00') + '</span>';
    var merch = ' at ' + details.merchant_name;
    var manu = details.manufacturer_name;    
    if(details.merchant_name == undefined || details.merchant_name == ''){ merch = ''; }
    if(details.manufacturer_name == undefined || details.manufacturer_name == ''){ manu = ''; }
    var size_div = colors_hash.color_names.length > 1 ? '<span class="sizing"><em></em> <strong>more colors available</strong></span>' : '' ;
    var rack_link = '<a href="#" class="add-to-rack" data-productid="' + 
      details.id + '"><i class="icon-hanger"></i>add to rack</a>';
    var rack_sku = details.id + '_' + details.merchant_id + '_' + details.product_id + '_' + details.sku;
    var rack_idx = rack_builder.rack_product_ids.indexOf(rack_sku);
    if(rack_idx > -1){
      rack_link = '<a href="#" class="add-to-rack selected" data-productid="' + 
        details.id + '"><i class="fa fa-check"></i> in rack</a>';
    }
    var fave_link = '<a href="#" class="favorite" data-productid="' + 
      details.id + '"><i class="fa fa-heart-o"></i></a>';
    var fave_idx = rack_builder.favorites_product_ids.indexOf(details.id);
    if(fave_idx > -1){
      var favorite_object = rack_builder.favorites[fave_idx];
      fave_link = '<a href="#" class="favorite favorited" data-productid="' + 
      details.id + '" data-faveid="' + favorite_object.id + '"><i class="fa fa-heart"></i></a>';
    }
    return '<div class="item"><div class="image">' + fave_link + 
      '<a href="#" class="item-detail" data-name="' + details.product_name + 
      '" data-brand="' + details.manufacturer_name + 
      '" data-productid="' + details.id + '" data-merchantid="' + details.merchant_id + 
      '"><img src="' + details.product_image_url + '"><span>view details</span></a>' +
      size_div + '</div><a href="' + details.product_url + '"  title="' + details.product_name + 
      '" target="_blank" class="name">' + details.product_name + '</a><span class="manu"' + 
      ' title="' + manu + '' + merch + '">' + manu + '' + merch + 
      '</span>' + price_display + '' + rack_link + '</div>';
  },
  /**
  * @description ajax call to get search results
  * @param {integer} page - the page to fetch
  * @param {boolean} lastSearch - boolen is performSearh is being called via cookie
  * @param {object} additionalCriteria - other search settings if from cookie
  */
  performSearch: function(page, lastSearch, additionalCriteria){
    $('#facet-bar').removeClass('show');
    /* generate the query string */
    var selection_markup = [];
    var facets = [];
    var q = '';
    var search_box = $('#search-field');
    var new_search = false;
    var text = search_box.val();
    var category = $('#search-categories').val();    
    if(text != '') { 
      selection_markup.push(
        '<a href="#" class="remove-search">' + text + '<i class="fa fa-times-circle"></i></a>'
      );
    }
    if(text != search_box.data('lookup')){
      search_box.data('lookup', text);
      /* no longer is a search text change a new search 4/25
      /* new_search = true;
      */
    }
    if(category != search_box.data('cat')){
      new_search = true;
      search_box.data('cat', category)
    }
    /**
    * if this a search instantiated from the cookie, we need
    * to set new_search to false so we can prevent categories with
    * client data from poluting the query param from the cookie
    */
    if(lastSearch == true){ new_search = false; }
    if(category != ''){
      facets.push('&primary_category=' + category);
      selection_markup.push(
        '<a href="#" class="remove-category" data-qparam="primary_category" ' +
        'data-facet="' + category + '">' + category + 
        '<i class="fa fa-times-circle"></i></a>'
      );
      /**
      * if it is a new search we need to see if we have any client
      * data to prepopulate some of our facets with
      */
      if(new_search == true){
        var sizes = [];
        var cleaned_sizes = [];
        if(["Jeans", "Shoes", "Tops", "Pants", "Bottoms", "Dresses"].indexOf(category) > -1){
          if(utils.category_settings == null){
            sizes = client_360.categories[category].size.split(','); 
          }else{
            var key_match = category == "Jeans" ? 'Bottoms' : category ;
            for(key in utils.category_settings){
              if(utils.category_settings.hasOwnProperty(key)){
                if(key == key_match){
                  if(utils.category_settings[key] != undefined){
                    for(var i = 0, l = utils.category_settings[key].length; i<l; i++){
                      var row = utils.category_settings[key][i];
                      if(['size: ','Bottoms size: '].indexOf(row.q) > -1){
                        if(row.a != null){
                          sizes = row.a.split(',');
                        }
                      } 
                    }
                  }
                }
              }
            }
          }  
        }
        for(i = 0, l = sizes.length; i<l; i++){
          var size = sizes[i];
          size = size.replace(/\s/g, "");
          cleaned_sizes.push(size);
        }
        var allume_sizes = search_page.getAllumSizes(cleaned_sizes, category);
        var id_mod = 'nosize';
        if(category == 'Shoes'){
          id_mod = 'shoe';
        }else if(["Shoes","Accessories","Other","Beauty","Unsure"].indexOf(category) == -1){
          id_mod = 'clothing';
        }
        for(i = 0, l = allume_sizes.length; i<l; i++){
          var size = allume_sizes[i];
          var size_group = '#sizegroup' + id_mod + '' + size.replace('.','');
          selection_markup.push(
            '<a href="#" class="remove-facet size" data-sizegroup="' + size_group + 
            '">' + size + '<i class="fa fa-times-circle"></i></a>'
          );
        }
        search_box.data('clientsize', allume_sizes.join('|')).data('clientsettings', true);
      }
    }else{
      
    }
    if(new_search == false){
      $.each($('#facets div.facet-list'), function(idx){
        var list = $(this);
        if(list.hasClass('size') == false){
          var qparam = list.data('qparam');
          var selected = list.find('input:checked');
          if(selected.length > 0){
            var values = selected.map(function (i, facet){ 
              selection_markup.push(
                '<a href="#" class="remove-facet" data-qparam="' + qparam + 
                '" data-facet="' + facet.value + '">' + facet.value + 
                '<i class="fa fa-times-circle"></i></a>'
              );
              return facet.value 
            }).get();
            facets.push(
              '&' + qparam + '=' + encodeURIComponent(values.join('|'))
            );
          }
        }else{
          /* special processing for size facets */
          var size_params = [];
          $.each(list.find('input.allume-size:checked'), function(ix){
            var size = $(this);
            selection_markup.push(
              '<a href="#" class="remove-facet size" data-sizegroup="' + size.data('groupdiv') + 
              '">' + size.val() + '<i class="fa fa-times-circle"></i></a>'
            );
            $.each($(size.data('groupdiv')).find('input.size-member:checked'), function(j){
              size_params.push($(this).val())
            });
          });
          /* get unique list of szie params */
          var clean_size_params = [...new Set(size_params)];
          if(clean_size_params.length > 0){
            //console.log(clean_size_params.join('|'))
            facets.push(
              '&size=' + encodeURIComponent(clean_size_params.join('|'))
            )
          }
        }
      });
    }
    /**
    * if this is a search from the cookie,
    * set new_search back to true and process the query param
    * facets from the cookie
    */
    if(lastSearch == true){
      new_search = true;
      var keys = Object.keys(additionalCriteria);
      for(var i = 0, l = keys.length; i<l; i++){
        var key = keys[i];
        if (key == 'sort') {
          $('#sort-dd')[0].selectize.setValue(additionalCriteria[key], true);
        } else if (key == 'size') {
          var terms = additionalCriteria[key].split('|');
          var allume_sizes = search_page.getAllumSizes(terms, category);
          var id_mod = 'nosize';
          if(category == 'Shoes'){
            id_mod = 'shoe';
          }else if(["Shoes","Accessories","Other","Beauty","Unsure"].indexOf(category) == -1){
            id_mod = 'clothing';
          }
          for(ix = 0, lx = allume_sizes.length; ix<lx; ix++){
            var size = allume_sizes[ix];
            var size_group = '#sizegroup' + id_mod + '' + size.replace('.','');
            selection_markup.push(
              '<a href="#" class="remove-facet size" data-sizegroup="' + size_group + 
              '">' + size + '<i class="fa fa-times-circle"></i></a>'
            );
          }
          search_box.data('clientsize', allume_sizes.join('|')).data('clientsettings', true);
        } else if (['page', 'text', 'primary_category','size'].indexOf(key) == -1) {
          var terms = additionalCriteria[key].split('|');
          for(var ix = 0, lx = terms.length; ix < lx; ix++){
            var term = terms[ix];
            selection_markup.push(
              '<a href="#" class="remove-facet" data-qparam="' + key + 
              '" data-facet="' + term + '">' + term + 
              '<i class="fa fa-times-circle"></i></a>'
            );
          }
        }
      }
    }
    q += 'page=' + page + '' + facets.join('');
    var faves = $('#facet-show-faves').prop('checked');
    if(faves == true){
      q += '&favs=' + parseInt($('#stylist').data('stylistid'));
    }
    $('#search-form-selections').html(selection_markup.join(''));
    if(selection_markup.length > 0){
      $('#facet-bar').addClass('show');
    }
    var sort_value = $('#sort-dd').val();
    if((sort_value != '')&&(sort_value != ' ')){
      q += '&sort=' + sort_value;
    }
    /* set the session search cookie so search will persist */
    if(text != '') { 
      var text_term = '&text=' + encodeURIComponent(text);
      q += text_term; 
    }
    var saved_search = q;
    utils.createCookie('lastShoppingToolSearch' + search_page.session_id, saved_search, 1);
    /* async call to get search results */
    $.ajax({
      beforeSend: function(){
        $('#results').html(
          '<div class="loader">' +
          '<span class="pulse_loader"></span>' +
          '<span class="pulse_message">Finding things you\'ll love...</span>' +
          '</div>'
        );
        $('#sort-selection').hide();
        $('#pager-message').html('');
        $('#pager').html('');
        if(new_search == true){
          $('#facets').html('');
        }        
      },
      type: "GET",
      url: '/product_api/facets?',
      data: q,
      success: function(results){
        if(new_search == false){
          if(results.data != undefined && results.data.length > 0){
            utils.pagerTemplate(results.page, results.total_items, results.num_per_page);
          }
          search_page.resultTemplate(results.data);
        }
        if(new_search == true){
          search_page.facetTemplate(results.facets, category);
          /**
          * if search from cookie we need to correctly 'check'
          * the facet values to mirror those in the cookie
          */
          if(lastSearch == true){
            var keys = Object.keys(additionalCriteria);
            for(var i = 0, l = keys.length; i<l; i++){
              var key = keys[i];
              if(['page', 'text', 'primary_category', 'sort', 'size'].indexOf(key) == -1){
                var facet_block = $('#facets div.facet-list[data-qparam="' + key + '"]');
                var terms = additionalCriteria[key].split('|');
                for(var ix = 0, lx = terms.length; ix < lx; ix++){
                  var term = terms[ix];
                  facet_block.find('input[value="' + term + '"]').prop('checked', true);
                }
              } else if (key == 'size') {

              }
            }
          }
          /* trigger the secondary fetch */
          $('#search-btn').trigger('click');
        }
      }
    });
  },
  /**
  * @description processing and template for product results
  * @param {array} results - the product result array
  */  
  resultTemplate: function(results){
    var markup = [];
    if(results != undefined && results.length > 0){
      for(var i = 0, l = results.length; i<l; i++){
        markup.push(
          search_page.itemTemplate(
            results[i]._source, 
            'list', 
            results[i].inner_hits.collapsed_by_product_name.hits.hits
          )
        );
      }
      $('#results').html(markup.join(''));
      if(markup.length > 0){
        var items = $('#results div.item');
        for(var i = 0, l = results.length; i<l; i++){
          var item = results[i];
          var details = item._source;  
          var inner_hits = item.inner_hits.collapsed_by_product_name.hits.hits; 
          var dom = items.eq(i)
          dom.find('a.add-to-rack').data('details',details);
          dom.find('a.favorite').data('details',details); 
          /* add the details and inner hits to the item-details dataset */
          dom.find('a.item-detail').data('hits', inner_hits).data('details', details)
        }
      }
      utils.equalHeight($('#results div.item'));
      $('#sort-selection').show()
    }else{
      $('#results').html('<div class="no-results">There were no products matching your supplied criteria...</div>');
    }
  },
  /**
  * @description size facet template function
  * @param {string} category - the current search category
  * @returns {string} HTML - size facet markup
  */
  sizeFacetTemplate: function(category){
    var size_block = facet_sizing;
    if(search_page.cached_sizes != null){
      size_block = search_page.cached_sizes.mapped;
    }
    /* data for the user size selections and preference */
    var cs = $('#search-field').data();
    /* process the sizes for facet display */
    var allume_sizes = cs.clientsettings == true ? cs.clientsize.split('|') : [] ;
    /* Template private helper functions */
    /**
    * @description private helper function to create size group HTML
    * @param {string} group - group name
    * @param {string} checked - check box checked value
    * @param {string} id_modifier - string to modify the size group ids 
    * @returns {string} HTML
    */
    function sizeGroup(group, checked, id_modifier){
      return '<div class="size-grouping-wrapper">' + 
        '<a href="#sizegroup' + id_modifier + 
        '' + group.replace(' ','').replace('.','') + '" class="size-group-toggle"><span>+</span></a>' +
        '<label class="size-grouping">' +
        '<input class="allume-size" type="checkbox" value="' + 
        group + '" ' + checked + ' data-sizegroup="' + 
        group.replace(' ','').replace('.','') + '" data-groupdiv="#sizegroup' + id_modifier + 
        '' + group.replace(' ','').replace('.','') + '"/><span><i class="fa fa-square-o"></i>' +
        '<i class="fa fa-check-square"></i>' +
        '</span><em class="key">' + group + '</em></label>' +
        '<div class="sizegroup-list" id="sizegroup' + 
        id_modifier + '' + group.replace(' ','').replace('.','') + '">';
    }
    /**
    * @description private helper function to create size group memberHTML
    * @param {object} member - member of size group
    * @param {string} checked - check box checked value
    * @returns {string} HTML
    */
    function sizeGroupMember(member, checked){
      return '<label class="size-facet"><input class="size-member" type="checkbox" value="' + 
        member.size + '" ' + checked + '/><span><i class="fa fa-circle-thin"></i>' +
        '<i class="fa fa-check-circle"></i></span><em class="key">' + member.name + '</em></label>';
    } 
    /**
    * @description private helper function to generate sub section markup
    * @param {array} sizes - array of sizes to process
    * @param {object} member_hash - member hash to get member lists  
    * @param {string} id_modifier - string to modify the size group ids 
    * @returns {string} HTML
    */
    function sizeSubsection(section_sizes, member_hash, id_modifier){
      var sectional = [];
      for(var i = 0, l = section_sizes.length; i<l; i++){
        var size_grouping = section_sizes[i];
        var sizes = member_hash[size_grouping].sizes;
        var size_members = member_hash[size_grouping].members;
        var checked = '';
        for(var ix = 0, lx = allume_sizes.length; ix<lx; ix++){
          var allume_size = allume_sizes[ix];
          for(var j = 0, n = sizes.length; j<n; j++){
            if( sizes[j] == allume_size ){
              checked = 'CHECKED'
            }
          }
        }
        sectional.push(sizeGroup(size_grouping, checked));
        for(var ix = 0, lx = size_members.length; ix<lx; ix++){
          var member = size_members[ix];
          sectional.push(sizeGroupMember(member, checked, id_modifier));
        }
        /* close the sizegroup, and wrapper div */
        sectional.push('</div></div>');
      }
      return sectional.join('');
    }
    /* size facet markup */
    var markup = [
      '<a href="#" class="facet-group"><span>+</span>Size</a>',
      '<div class="facet-list size" data-qparam="size">'
    ];    
    /* create correct size facets HTML based upon category */
    if (category == ''){
      /* shoe sizes */
      markup.push(
        '<a href="#" class="size-facet-sub"><span>+</span>Clothing (Regular Sizes)</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.regular_sizes, size_block.clothing_members, 'clothing') + '</div>' +
        '<a href="#" class="size-facet-sub"><span>+</span>Clothing (Petite Sizes)</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.petite_sizes, size_block.clothing_members, 'clothing') + '</div>' +
        '<a href="#" class="size-facet-sub"><span>+</span>Clothing (Tall Sizes)</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.tall_sizes, size_block.clothing_members, 'clothing') + '</div>' +        
        '<span class="size-breaker"></span>' +        
        '<a href="#" class="size-facet-sub"><span>+</span>Shoes (Regular Sizes)</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.regular_shoes, size_block.shoe_members, 'shoe') + '</div>' +
        '<a href="#" class="size-facet-sub"><span>+</span>Shoes (Narrow Sizes)</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.narrow_shoes, size_block.shoe_members, 'shoe') + '</div>' +      
        '<a href="#" class="size-facet-sub"><span>+</span>Shoes (Wide Sizes)</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.wide_shoes, size_block.shoe_members, 'shoe') + '</div>' +
        '<span class="size-breaker"></span>' + 
        '<a href="#" class="size-facet-sub"><span>+</span>One Size</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.one_size, size_block.clothing_members, 'nosize') + '</div>'
      );
    }else if (category == 'Shoes'){
      /* shoe sizes */
      markup.push(
        '<a href="#" class="size-facet-sub"><span>+</span>Shoes (Regular Sizes)</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.regular_shoes, size_block.shoe_members, 'shoe') + '</div>' +
        '<a href="#" class="size-facet-sub"><span>+</span>Shoes (Narrow Sizes)</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.narrow_shoes, size_block.shoe_members, 'shoe') + '</div>' +      
        '<a href="#" class="size-facet-sub"><span>+</span>Shoes (Wide Sizes)</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.wide_shoes, size_block.shoe_members, 'shoe') + '</div>'
      ); 
    }else if(["Shoes","Accessories","Other","Beauty","Unsure"].indexOf(category) == -1){
      /* clothing sizes */
      markup.push(
        '<a href="#" class="size-facet-sub"><span>+</span>Clothing (Regular Sizes)</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.regular_sizes, size_block.clothing_members, 'clothing') + '</div>' +
        '<a href="#" class="size-facet-sub"><span>+</span>Clothing (Petite Sizes)</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.petite_sizes, size_block.clothing_members, 'clothing') + '</div>' +
        '<a href="#" class="size-facet-sub"><span>+</span>Clothing (Tall Sizes)</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.tall_sizes, size_block.clothing_members, 'clothing') + '</div>'
      );  
    }else{
      /* things with no size */
      markup.push(
        '<a href="#" class="size-facet-sub"><span>+</span>One Size</a>' +
        '<div class="size-facet-sub-group">' + 
        sizeSubsection(size_block.one_size, size_block.clothing_members, 'nosize') + '</div>'
      );
    }
    /* add in the unmapped sizes */
    if(search_page.cached_sizes != null){
      var matching_unmapped_category = search_page.cached_sizes.unmapped[category];
      if(matching_unmapped_category != undefined){

        markup.push(
          '<span class="size-breaker"></span>' +
          '<a href="#" class="size-facet-sub"><span>+</span>One Size</a>' +
          '<div class="size-facet-sub-group">' + 
          '<div class="size-grouping-wrapper">' + 
          '<a href="#sizegroupunmapped" class="size-group-toggle"><span>+</span></a>' +
          '<label class="size-grouping">' +
          '<input class="allume-size unmap" type="checkbox" value="" data-sizegroup="unmapped" ' +
          'data-groupdiv="#sizegroupunmapped"/><span><i class="fa fa-square-o"></i>' +
          '<i class="fa fa-check-square"></i>' +
          '</span><em class="key">Unmapped ' + category + ' sizes</em></label>' +
          '<div class="sizegroup-list" id="sizegroupunmapped">'
        );

        for(var i = 0, l = matching_unmapped_category.length; i<l; i++){
          var unmap_size = matching_unmapped_category[i];
          var unmap_check = allume_sizes.indexOf(unmap_size) > -1 ? 'checked' : '' ;
          markup.push(
            '<label class="size-facet"><input class="size-member" type="checkbox" value="' + 
            unmap_size + '" ' + unmap_check + '/><span><i class="fa fa-circle-thin"></i>' +
            '<i class="fa fa-check-circle"></i></span><em class="key">' + unmap_size + '</em></label>'
          );
        }
        markup.push('</div></div></div>');
      }
      
    }
    return markup.join('') + '</div>';
  }
}