/**
* @description search_page namespace object, conatining the functionality and templates for the search page
*/
var search_page = {
  /** 
  * @description cache of styling session
  */
  session_id: '',
  /**
  * @description add to rack functionality
  * @param {DOM object} item - link clicked
  */
  addToRack: function(item){
    var rack = $('#rack-list');
    var existing = rack.data('skus');
    var details = item.data('details');
    var idx = item.closest('div.item').index();
    var items = rack.find('div.item').length;
    var sku = details.id + '_' + details.merchant_id + '_' + details.product_id + '_' + details.sku;
    var add_to_list = false;
    if(existing == undefined){
      item.addClass('selected').html('<i class="fa fa-check"></i> added to rack');
      rack.data('skus', details.sku);
      add_to_list = true;
    }else{
      existing = existing.split(',');
      if(existing.indexOf(sku) == -1){
        existing.push(sku);
        rack.data('skus', existing.join(','));
        item.addClass('selected').html('<i class="fa fa-check"></i> added to rack');
        add_to_list = true;
      }
    }
    if(add_to_list == true){
      if(items == 0){rack.html('');}
      var obj = {
        product: parseInt(details.id),
        allume_styling_session: parseInt(search_page.session_id)
      }
      console.log(JSON.stringify(obj))
      $.ajax({
        contentType : 'application/json',
        data: JSON.stringify(obj),
        success:function(response){
          rack.append(search_page.itemTemplate(details, 'rack', idx, response.id));
          search_page.updateRackCount();
        },
        type: 'PUT',
        url: '/shopping_tool_api/rack_item/0/'
      })
    }else{
      var pos = item.offset();
      if($('#air-' + idx).length < 1){
        $('body').append(
          '<div class="already-in-rack" id="air-' + idx + 
          '" style="top:' + (pos.top - 32) + 'px;left:' + (pos.left - 37) + 
          'px"><span class="msg">SKU already in rack</span>' +
          '<span class="tail"></span></div>'
        )
        var id = 'air-' + idx;
        window.setTimeout(function(){
          $('#' + id).fadeOut(function(){
            $('#' + id).remove();
          })
        }, 3000)
      }
    }
  },
  /**
  * @description capitalize the first letter of a string
  * @param {string} str - the string to process
  * @returns {string} capitalized first letter of the same string
  */
  capitalizeFirstLetter: function(str){
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  },  
  /**
  * @description capitalize the first letter of every word in a string
  * @param {string} str - the string to process
  * @returns {string} fixed string
  */
  capitalizeEveryWord: function(str){
    return str.replace(/\w\S*/g, function(txt){
      return search_page.capitalizeFirstLetter(txt);
    });
  },
  /**
  * @description make a groups of DOM objects all the same height
  * @params {DOM Array} - array of DOM objects
  */
  equalHeight: function(group) {
    var tallest = 0;
    group.each(function() {
      var thisHeight = $(this).height();
      if(thisHeight > tallest) {
        tallest = thisHeight;
      }
    });
    group.height(tallest);
  },
  /**
  * @description init function applying the functionality to the page elements
  */
  init: function(){
    /* set rack existing products */
    var rack_list = $('#rack-list');
    var existing_items = [];
    $.each(rack_list.find('div.item'), function(idx){
      var item = $(this);
      existing_items.push(item.data('sku'));
    });
    rack_list.data('skus', existing_items.join(','));
    /* cache the session id */
    search_page.session_id = $('body').data('stylesession');
    /* add keyboard shortcuts for rack and client open/close */
    Mousetrap.bind('shift+z+x', function(e) {
      $('#rack').toggleClass('show');
      $('#look-list').toggleClass('show');
      return false;
    });
    Mousetrap.bind('shift+a+s', function(e) {
      $('#user-card').toggleClass('show')
      return false;
    });
    Mousetrap.bind('shift+q+w', function(e) {
      $('#new-look-error').html('');
      $('#new-look-name').val('');
      $('#new-look-layout')[0].selectize.setValue('',true);      
      $('#create-look').fadeToggle();
      return false;
    });    
    /* search functionality */
    $('#search-btn').click(function(e){
      e.preventDefault();
      search_page.performSearch(1);
    });
    $("#search-field").keyup(function(event) {
      if (event.keyCode === 13) {
        search_page.performSearch(1);
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
       search_page.performSearch(1);
    });
    $('#search-form-selections').on('click', 'a', function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('remove-search')){
        $('#search-field').val('');
        search_page.performSearch(1);
      }else{
        var facets = $('#facets');
        var facet = link.data('facet');
        var group = link.data('qparam');
        var group_div = facets.find('div[data-qparam="' + group + '"]');
        var facet_link = group_div.find('input[value="' + facet + '"]');
        facet_link.prop('checked', false);
        search_page.performSearch(1);
      }
    });
    /* results functionality */
    $('#results').on('click','a.favorite',function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('favorited')){
        link.removeClass('favorited').find('i').removeClass('fa-heart').addClass('fa-heart-o');
      }else{
        link.addClass('favorited').find('i').removeClass('fa-heart-o').addClass('fa-heart');
      }
      // ajax submission of favoriting will go here
    }).on('click','a.add-to-rack',function(e){
      e.preventDefault();
      var link = $(this);
      search_page.addToRack(link);
    }).on('mouseenter', 'a.info-toggle', function(e){
      var link = $(this);
      var tt = link.siblings('div.tt');
      tt.addClass('check')
      var h = tt.height()
      tt.removeClass('check');
      var pos = link.position();
      tt.css({top: (pos.top - (h + 20)) +'px', left: (pos.left - 174) + 'px'}).fadeIn()
    }).on('mouseleave', 'a.info-toggle', function(e){
      var link = $(this);
      var tt = link.siblings('div.tt'); 
      tt.fadeOut();  
    });
    /* pager functionality */
    $('#pager').on('click','a.page',function(e){
      e.preventDefault();
      var link = $(this);
      search_page.performSearch(parseInt(link.data('page')));
      $('html,body').animate({ scrollTop: 0 }, 300);
    });
    /* my rack functionality */
    $('#rack-toggle').click(function(e){
      e.preventDefault();
      $('#rack').toggleClass('show');
      $('#look-list').toggleClass('show');
    });
    $('#close-rack').click(function(e){
      e.preventDefault();
      $('#rack').removeClass('show');
      $('#look-list').removeClass('show');
    });
    $('#rack-list').on('click','a.remove-from-rack',function(e){
      e.preventDefault();
      var link = $(this);
      var sku = link.data('sku');
      var rack = $('#rack-list');
      var existing = rack.data('skus').split(',');
      var idx = existing.indexOf(sku);
      existing.splice(idx,1);
      rack.data('skus',existing.join(','));
      if(link.hasClass('at-load') == false){
        /* undo selected btn */
        var list_entry = $('#results div.item').eq(link.data('idx'));
        var add_link = list_entry.find('a.add-to-rack');
        var details = add_link.data('details')
        var link_sku = details.id + '_' + details.merchant_id + '_' + details.product_id + '_' + details.sku;
        if(link_sku == sku){
          add_link.html('<i class="icon-hanger"></i>add to rack').removeClass('selected');
        }        
      }
      $.ajax({
        success:function(response){
          link.closest('div.item').remove();
          /* add user friendly markup if rack is empty */
          if(rack.find('div.item').length == 0){
            rack.html('<div class="empty">Add items to your rack...</div>');
          }
          search_page.updateRackCount();
        },
        type: 'DELETE',
        url: '/shopping_tool_api/rack_item/' + link.data('rackid') + '/'
      });
    });
    $('#add-look-btn').click(function(e){
      e.preventDefault();
      $('#new-look-error').html('');
      $('#new-look-name').val('');
      $('#new-look-layout')[0].selectize.setValue('',true);
      $('#create-look').fadeIn();
    });
    $('#look-links').on('click', 'a.look-link', function(e){
      e.preventDefault();
      var link = $(this);
      look_builder.setUpBuilder(link.data('lookid'))
      $('#designing').html(link.data('lookname'));
      $('#design-look').attr('class','').addClass('show');
    });
    /* client details functionality */
    $('#user-clip').delay(750)
      .queue(function (next) { 
        $(this).addClass('ready').width($('#user-clip span.name').width()); 
        next(); 
      });
    $('#user-clip').click(function(e){
      e.preventDefault();
      $('#user-card').toggleClass('show')
    });
    /* new look create form */
    $('#new-look-layout').selectize({
      valueField: 'id',
      labelField: 'name',
      searchField: 'name',
      options: look_layouts,
      create: false,
      render: {
        option: function(item, escape) {
          return '<div class="layout-option">' +
            '<span class="name">' + escape(item.name) + '</span>' +
            '<span class="columns">columns: ' + escape(item.columns) + '</span>' +
            '<span class="rows">rows: ' + escape(item.rows) + '</span>' +
            '</div>';
        }
      }
    });
    $('#cancel-new-look').click(function(e){
      e.preventDefault()
      $('#create-look').fadeOut();
    });
    $('#create-new-look').click(function(e){
      $('#new-look-error').html('');
      e.preventDefault();
      var pre = 0;
      var msg = [];
      var look_obj = {
       "name": $('#new-look-name').val(),
       "look_layout": parseInt($('#new-look-layout').val()),
       "allume_styling_session": search_page.session_id,
       "stylist": parseInt($('#stylist').data('stylistid'))        
      }
      if(look_obj.name == ''){ 
        pre++; 
        msg.push('provide a look name'); 
      }
      if(isNaN(look_obj.look_layout)){ 
        pre++; 
        msg.push('select a look layout'); 
      }
      if(pre == 0){
        $.ajax({
          contentType : 'application/json',
          data: JSON.stringify(look_obj),
          success:function(response){
            look_builder.newLookLink(response);
            $('#create-look').fadeOut();
          },
          type: 'PUT',
          url: '/shopping_tool_api/look/0/'
        })
      }else{
        $('#new-look-error').html(
          '<span><i class="fa fa-exclamation-circle"></i>' +
          'You must ' + msg.join('; ') + 
          '.</span>'
        );
      }
    }); 
    look_builder.functionality(); 
  },
  /**
  * @description processing and template for facets
  * @param {object} facets - the facets object
  */
  facetTemplate: function(facets){
    var markup = [];
    if(facets != undefined){
      var social_facets = [];
      var group_markup = {names: [], markup: {}}
      /* build initial list of facet buckets */
      var buckets = Object.keys(facets);
      for(var i = 0, l = buckets.length; i<l; i++){
        var bucket = buckets[i];
        var facet_list = facets[bucket];
        if(['_filter_is_best_seller', '_filter_is_trending'].indexOf(bucket) == -1){
          var display_name = bucket.replace('_filter_', '');
          group_markup.names.push(display_name);
          group_markup.markup[display_name] = [];
          group_markup.markup[display_name].push(
            '<a href="#" class="facet-group"><span>+</span>' + 
            search_page.capitalizeEveryWord(display_name.replace(/_/g, ' ')) + 
            '</a><div class="facet-list" data-qparam="' + display_name + '">'
          );
          facet_list[display_name].buckets.sort(function(a,b){
            if(a.key.toLowerCase() > b.key.toLowerCase()){ return 1}
            if(a.key.toLowerCase() < b.key.toLowerCase()){ return -1}
            return 0;
          })
          for(var j = 0, num = facet_list[display_name].buckets.length; j<num; j++){
            var facet = facet_list[display_name].buckets[j];
            if(facet.key != ''){
              group_markup.markup[display_name].push(
                '<label class="facet">' +
                '<input class="facet-box" type="checkbox" value="' + 
                facet.key + '" data-facetgroup="' + display_name + '"/><span>' +
                '<i class="fa fa-circle-thin"></i>' +
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
      group_markup.names.sort();
      for(var i = 0, l = group_markup.names.length; i<l; i++){
        var group_name = group_markup.names[i];
        markup.push(group_markup.markup[group_name].join(''));
      }
      $('#facets').html(markup.join(''));
    }    
  },
  /**
  * @description item template for results and rack
  * @param {object} details - item details JSON
  * @param {string} view - which display
  * @param {integer} idx - list idx used in 'rack' view
  * @param {integer} rack_item_id - list idx used in 'rack' view  
  * @returns {string} HTML
  */   
  itemTemplate: function(details, view, idx, rack_item_id){
    var w = $('#results').width() / 3
    var dynamic_dim = 'style="width:' + (w - 15) + 'px;"'    
    var desc = details.long_product_description == '' ? details.short_product_description : details.long_product_description ;
    var retail = details.retail_price;
    var sale = details.sale_price;
    var price_display = '';
    var merch = '<span class="merch">' + details.merchant_name + '</span>';
    var manu = '<span class="manu">by ' + details.manufacturer_name + '</span>';    
    if((sale >= retail)||(sale == 0)){
      price_display = '<span class="price">' + numeral(retail).format('$0,0.00') + '</span>';
    }else{
      price_display = '<span class="price"><em>(' + numeral(retail).format('$0,0.00') + 
        ')</em>' + numeral(sale).format('$0,0.00') + '</span>';
    }
    if(details.merchant_name == undefined || details.merchant_name == ''){ merch = ''; }
    if(details.manufacturer_name == undefined || details.manufacturer_name == ''){ manu = ''; }
    if(view == 'list'){
      return '<div class="item"><div class="image"><a href="#" class="favorite">' +
        '<i class="fa fa-heart-o"></i></a><img src="' + 
        details.product_image_url + '" ' + dynamic_dim + '></div><a href="' + details.product_url + 
        '" target="_blank" class="name">' + details.product_name + '</a>' + 
        '<a href="#" class="add-to-rack" data-productid="' + details.id + 
        '"><i class="icon-hanger"></i>add to rack</a>' + merch + 
        '' + manu + '<a href="#" class="info-toggle"><i class="fa fa-info-circle"></i></a>' + 
        price_display + '<div class="tt"><span><em>size:</em>' + 
        details.size + '</span><span><em>description:</em>' + details.short_product_description + 
        '</span></div></div>';
    }else{
      return '<div class="item" data-productid="' + details.id + '" title="' + details.merchant_name + ' by ' + 
        details.manufacturer_name + '"><a href="#" class="remove-from-rack" data-sku="' + 
        details.id + '_' + details.merchant_id + '_' + details.product_id + '_' + details.sku + 
        '" data-idx="' + idx + '" data-productid="' + details.id + '" data-rackid="' + 
        rack_item_id + '"><i class="fa fa-times"></i></a>' +
        '<div class="image"><img src="' + details.product_image_url + 
        '"/></div><div class="details">' + price_display + '</div></div>';
    }
  },
  /**
  * @description processing and template for pagination of results
  * @param {integer} page - page currently displayed
  * @param {integer} total - total number of items in result set
  * @param {integer} per_page - number of items per page payload
  */  
  pagerTemplate: function(page, total, per_page){
    var markup = [];
    var total_pages = Math.floor(total / per_page);
    var excess = total % per_page;
    if(excess > 0){ total_pages++};
    /* create pager message string */
    var showing_low = numeral(((page * per_page) - per_page + 1)).format('0,0');
    var showing_high = numeral(page * per_page).format('0,0');
    if(total < per_page){
      showing_high = numeral(total).format('0,0');
    }
    var result_total = numeral(total).format('0,0');
    $('#pager-message').html(
      'Showing <strong>' + showing_low + '</strong> - <strong>' + 
      showing_high + '</strong> of <strong>' + result_total + '</strong>'
    );
    /**
    * @description private function to gerenate links
    * @param {integer} page - current page
    * @param {integer} low - low number to use in loop
    * @param {integer} high - high number to use in loop
    * @returns {string} HTML
    */        
    function makePager(page, low, high){
      var pager = [];
      for(var i = (page - low); i < (page + high); i++){
        if(i > 0){        
          if(i == page){
            pager.push('<span class="current">' + i + '</span>');
          }else{
            if(i <= total_pages){
              pager.push('<a href="#" data-page="' + i + '" class="page">' + i + '</a>');
            }
          }
        }
      }
      return pager.join('');
    }
    if(page > 1){
      markup.push(
        '<a href="#" data-page="' + (page - 1) + 
        '" class="page prev"><i class="fa fa-angle-left"></i>Previous</a>'
      );
    }
    if(total_pages > page){
      markup.push(
        '<a href="#" data-page="' + (page + 1) + 
        '" class="page next">Next<i class="fa fa-angle-right"></i></a>'
      );
    }
    if((page > 3)&&(page <= (total_pages - 3))){
      markup.push(
        '<a href="#" data-page="1" class="page">1</a>' +
        '<span class="break">...</span>' +
        makePager(page, 1, 2)
      );
      if((page + 2) < total_pages){
        markup.push(
          '<span class="break">...</span>' +
          '<a href="#" data-page="' + total_pages + '" class="page">' + total_pages + '</a>'
        )          
      }
    }else{
      var show_max_ellipse = false;
      if(page == 1){
        var max = total_pages > 5 ? 4 : 5;
        markup.push(
          makePager(page, 2, max)
        );
        if((page + max) < total_pages){ show_max_ellipse = true }
      }else if(page == 2){
        var max = total_pages > 5 ? 3 : 4;
        markup.push(
          makePager(page, 1, max)
        );  
        if((page + max) < total_pages){ show_max_ellipse = true }              
      }else if(page == 3){
        var max = total_pages > 5 ? 2 : 3;
        markup.push(
          makePager(page, 2, max)
        );
        if((page + max) < total_pages){ show_max_ellipse = true } 
      }else if(page == total_pages){
        var min = 2; 
        if(total_pages > 5){ min = 3 }else if(total_pages <= 5){ min = 4}; 
        if((page - min) > 2 ){
          markup.push(
            '<a href="#" data-page="1" class="page">1</a>' +
            '<span class="break">...</span>'
          );
        } 
        markup.push(
          makePager(page, min , 2)
        );       
      }else if(page == (total_pages - 1)){
        var min = 3; 
        if(total_pages > 5){ min = 2 }else if(total_pages <= 5){ min = 3}; 
        if((page - min) > 2 ){
          markup.push(
            '<a href="#" data-page="1" class="page">1</a>' +
            '<span class="break">...</span>'
          );
        } 
        markup.push(
          makePager(page, min , 2)
        );       
      }else if(page == (total_pages - 2)){
        var min = 4; 
        if(total_pages > 5){ min = 1 }else if(total_pages <= 5){ min = 2}; 
        if((page - min) > 2 ){
          markup.push(
            '<a href="#" data-page="1" class="page">1</a>' +
            '<span class="break">...</span>'
          );
        } 
        markup.push(
          makePager(page, min , 3)
        );       
      }
      if(show_max_ellipse == true){
        markup.push(
          '<span class="break">...</span>' +
          '<a href="#" data-page="' + total_pages + '" class="page">' + total_pages + '</a>'
        );
      }
    }
    $('#pager').html(markup.join(''));
  },
  /**
  * @description ajax call to get search results
  * @param {integer} page - the page to fetch
  */
  performSearch: function(page){
    $('#facet-bar').removeClass('show');
    /* generate the query string */
    var selection_markup = []
    var q = '';
    var search_box = $('#search-field');
    var new_search = false;
    var text = search_box.val();
    if(text != '') { 
      q += 'text=' + encodeURIComponent(text); 
      selection_markup.push(
        '<a href="#" class="remove-search">' + text + '<i class="fa fa-times-circle"></i></a>'
      );
    }
    if(text != search_box.data('lookup')){
      search_box.data('lookup', text);
      new_search = true;
    }
    var facets = [];
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
    q += '&page=' + page + '' + facets.join('');
    console.log('query string: ' + q)
    $('#search-form-selections').html(selection_markup.join(''));
    if(selection_markup.length > 0){
      $('#facet-bar').addClass('show');
    }
    $.ajax({
      beforeSend: function(){
        $('#results').html(
          '<div class="loader">' +
          '<span class="pulse_loader"></span>' +
          '<span class="pulse_message">Finding things you\'ll love...</span>' +
          '</div>'
        );
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
        console.log(results)
        if(results.data != undefined && results.data.length > 0){
          search_page.pagerTemplate(results.page, results.total_items, results.num_per_page);
        }
        search_page.resultTemplate(results.data);
        if(new_search == true){
          search_page.facetTemplate(results.facets);
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
          items.eq(i).find('a.add-to-rack').data('details',details);       
        }
      }
      search_page.equalHeight($('#results div.item'));
    }else{
      $('#results').html('<div class="no-results">There were no products matching your supplied criteria...</div>');
    }
  },
  /**
  * @description update the rack toggle button display
  */
  updateRackCount: function(){
    var items = $('#rack-list div.item').length;
    var s = items == 1 ? '' : 's';
    $('#rack-toggle').html('<span>' + items + '</span> item' + s + ' in your rack');
    $('#rack-number').html(items + ' item' + s)
  }
}