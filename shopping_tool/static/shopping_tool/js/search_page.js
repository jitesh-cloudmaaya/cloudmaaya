/**
* @description search_page namespace object, conatining the functionality and templates for the search page
*/
var search_page = {
  /** 
  * @description cache of styling session
  */
  session_id: '',
  /**
  * @description init function applying the functionality to the page elements
  */
  init: function(){
    /* cache the session id */
    search_page.session_id = $('body').data('stylesession');
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
    })
    $('#search-categories').val('').selectize({ create: false, sortField: 'text'}).change(function(){
      var dd = $(this);
      var val = dd.val();
      var def_div = $('#client-defaults');
      var header = '<h5>Client preferences and sizes for <strong>' + val + '</strong>:</h5>';
      var general = '<span><em>colors:</em>' + client_360.colors + '</span>' +
        '<span><em>styles to avoid:</em>' + client_360.avoid + '</span>';
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
        def_div.html('');
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
      e.preventDefault();
      var box = $(this);
      var facet_links = $('#search-form-selections');
       search_page.performSearch(1, false, null);
    });
    $('#search-form-selections').on('click', 'a', function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('remove-search')){
        $('#search-field').val('');
        search_page.performSearch(1, false. null);
      }else if(link.hasClass('remove-category')){
        $('#search-categories')[0].selectize.setValue('',true);
        search_page.performSearch(1, false, null);
      }else{
        var facets = $('#facets');
        var facet = link.data('facet');
        var group = link.data('qparam');
        var group_div = facets.find('div[data-qparam="' + group + '"]');
        var facet_link = group_div.find('input[value="' + facet + '"]');
        facet_link.prop('checked', false);
        search_page.performSearch(1, false, null);
      }
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
      rack_builder.inspectItem(link, 'rack');
    });       
    /* check last search cookie and load if exists */
    var search_cookie = utils.readCookie('lastShoppingToolSearch' + search_page.session_id);
    if(search_cookie != null){
      var last_search = utils.parseQuery(search_cookie);
      var search_box = $('#search-field');
      var category = $('#search-categories');
      category[0].selectize.setValue(last_search.primary_category, false);
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
  */
  facetTemplate: function(facets){
    var markup = [];
    var cs = $('#search-field').data();
    if(facets != undefined){
      var social_facets = [];
      var group_markup = {names: [], markup: {}}
      /* build initial list of facet buckets */
      var display_order = ['_filter_size','_filter_price_range','_filter_brand',
                           '_filter_merchant_name','_filter_color','_filter_material'];
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
              }else if((pretty_name == 'price_range')&&(cs.clientsettings == true)){
                var spend = cs.clientspend.split('|');
                if(spend.indexOf(facet.key) > -1){
                  checked = "checked";
                }
              }
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
  * @description item template for results and rack
  * @param {object} details - item details JSON
  * @param {string} view - which display 
  * @returns {string} HTML
  */   
  itemTemplate: function(details, view){
    var w = $('#results').width() / 3;   
    var desc = details.long_product_description == '' ? details.short_product_description : details.long_product_description ;
    var price_display = '<span class="price">' + numeral(details.current_price).format('$0,0.00') + '</span>';
    var merch = ' at ' + details.merchant_name;
    var manu = details.manufacturer_name;    
    if(details.merchant_name == undefined || details.merchant_name == ''){ merch = ''; }
    if(details.manufacturer_name == undefined || details.manufacturer_name == ''){ manu = ''; }

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
      '"><img src="' + details.product_image_url + '"><span>view details</span></a></div>' +
      '<a href="' + details.product_url + '"  title="' + details.product_name + 
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
      new_search = true;
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
        var spend = [];
        var sizes = [];
        var cleaned_sizes = [];
        var cleaned_spend = [];
        if(["Dresses", "Jackets"].indexOf(category) > -1){
          spend = client_360.categories[category].spend.split(', ');       
        }else if(["Jeans", "Shoes", "Tops", "Pants", "Bottoms"].indexOf(category) > -1){
          spend = client_360.categories[category].spend.split(', ');
          sizes = client_360.categories[category].size.split(',');   
        }
        for(i = 0, l = sizes.length; i<l; i++){
          var size = sizes[i];
          size = size.replace(/\s/g, "");
          cleaned_sizes.push(size);
          selection_markup.push(
            '<a href="#" class="remove-facet" data-qparam="size" data-facet="' + 
            size + '">' + size + '<i class="fa fa-times-circle"></i></a>'
          );
        }
        for(i = 0, l = spend.length; i<l; i++){
          var range = spend[i].replace(/\$/g, '').split(' - ');
          var propper_range = '$' + range[0] + ' - $' + range[1];
          if(range[0] == '200+'){
            propper_range = '$200+';
          }
          cleaned_spend.push(propper_range);
          selection_markup.push(
            '<a href="#" class="remove-facet" data-qparam="price_range" data-facet="' + 
            propper_range + '">' + propper_range + '<i class="fa fa-times-circle"></i></a>'
          );
        }
        search_box.data('clientsize', cleaned_sizes.join('|')).data('clientspend', cleaned_spend.join('|')).data('clientsettings', true);
      }
    }
    if(new_search == false){
      $.each($('#facets div.facet-list'), function(idx){
        var list = $(this);
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
        if(key == 'sort'){
          $('#sort-dd')[0].selectize.setValue(additionalCriteria[key], true);
        }else if(['page', 'text', 'primary_category'].indexOf(key) == -1){
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
          search_page.facetTemplate(results.facets);
          /**
          * if search from cookie we need to correctly 'check'
          * the facet values to mirror those in the cookie
          */
          if(lastSearch == true){
            var keys = Object.keys(additionalCriteria);
            for(var i = 0, l = keys.length; i<l; i++){
              var key = keys[i];
              if(['page', 'text', 'primary_category', 'sort'].indexOf(key) == -1){
                var facet_block = $('#facets div.facet-list[data-qparam="' + key + '"]');
                var terms = additionalCriteria[key].split('|');
                for(var ix = 0, lx = terms.length; ix < lx; ix++){
                  var term = terms[ix];
                  facet_block.find('input[value="' + term + '"]').prop('checked', true);
                }
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
        markup.push(search_page.itemTemplate(results[i]._source, 'list'));
      }
      $('#results').html(markup.join(''));
      if(markup.length > 0){
        var items = $('#results div.item');
        for(var i = 0, l = results.length; i<l; i++){
          var item = results[i];
          var details = item._source;   
          var dom = items.eq(i)
          dom.find('a.add-to-rack').data('details',details);
          dom.find('a.favorite').data('details',details);     
        }
      }
      utils.equalHeight($('#results div.item'));
      $('#sort-selection').show()
    }else{
      $('#results').html('<div class="no-results">There were no products matching your supplied criteria...</div>');
    }
  }
}