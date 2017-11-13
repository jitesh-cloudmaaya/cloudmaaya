/**
* @description search_page namespace object, conatining the functionality and templates for the search page
*/
var search_page = {
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
    var add_to_list = false;
    if(existing == undefined){
      item.addClass('selected').html('<i class="fa fa-check"></i> added to rack');
      rack.data('skus', details.sku);
      add_to_list = true;
    }else{
      existing = existing.split(',');
      if(existing.indexOf(details.sku) == -1){
        existing.push(details.sku);
        rack.data('skus', existing.join(','));
        item.addClass('selected').html('<i class="fa fa-check"></i> added to rack');
        add_to_list = true;
      }
    }
    if(add_to_list == true){
      if(items == 0){rack.html('');}
      rack.append(search_page.itemTemplate(details, 'rack', idx));
      search_page.updateRackCount();
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
    /* add keyboard shortcuts for rack and client open/close */
    Mousetrap.bind('shift+z+x', function(e) {
      $('#rack').toggleClass('show');
      return false;
    });
    Mousetrap.bind('shift+a+s', function(e) {
      $('#user-card').toggleClass('show')
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
    })
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
    });
    $('#close-rack').click(function(e){
      e.preventDefault();
      $('#rack').removeClass('show');
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
      link.closest('div.item').remove();
      /* undo selected btn */
      var list_entry = $('#results div.item').eq(link.data('idx'));
      var add_link = list_entry.find('a.add-to-rack');
      var link_sku = add_link.data('details').sku;
      if(link_sku == sku){
        add_link.html('<i class="icon-hanger"></i>add to rack').removeClass('selected');
      }
      /* add user friendly markup if rack is empty */
      if(rack.find('div.item').length == 0){
        rack.html('<div class="empty">Add items to your rack...</div>');
      }
      search_page.updateRackCount();
    });
    $('#create-look').click(function(e){
      e.preventDefault()
      alert('this will take you to create look')
    })
    /* client details funcgionality */
    $('#user-clip').delay(750)
      .queue(function (next) { 
        $(this).addClass('ready').width($('#user-clip span.name').width()); 
        next(); 
      });
    $('#user-clip').click(function(e){
      e.preventDefault();
      $('#user-card').toggleClass('show')
    });
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
  * @returns {string} HTML
  */   
  itemTemplate: function(details, view, idx){
    var w = $('#results').width() / 3
    var dynamic_dim = 'style="width:' + (w - 15) + 'px;"'    
    var desc = details.long_product_description == '' ? details.short_product_description : details.long_product_description ;
    var retail = details.retail_price;
    var sale = details.sale_price;
    var price_display = '';
    var merch = '<span class="merch">' + details.merchant_name + '</span>';
    var manu = '<span class="manu">by ' + details.manufacturer_name + '</span>';    
    if((sale >= retail)||(sale == 0)){
      price_display = '<span class="price"><em>retail price</em>' + numeral(retail).format('$0,0.00') + 
      '</span><span class="price"><em>shipping</em>' + numeral(details.shipping_price).format('$0,0.00') + '</span>';
    }else{
      price_display = '<span class="price strike"><em>retail price</em>' + numeral(retail).format('$0,0.00') + 
      '</span><span class="price"><em>sale price</em>' + numeral(sale).format('$0,0.00') + '</span>' +
      '<span class="price"><em>shipping</em>' + numeral(details.shipping_price).format('$0,0.00') + '</span>';
    }
    if(details.merchant_name == undefined || details.merchant_name == ''){ merch = ''; }
    if(details.manufacturer_name == undefined || details.manufacturer_name == ''){ manu = ''; }
    if(view == 'list'){
      return '<div class="item"><div class="image"><a href="#" class="favorite">' +
        '<i class="fa fa-heart-o"></i></a><img src="' + 
        details.product_image_url + '" ' + dynamic_dim + '></div><span class="name">' + 
        details.product_name + '</span><span class="avail">' + details.availability + 
        '</span>' + merch + '' + manu + '' + price_display + '' + 
        '<span class="size"><em>size</em>' + details.size + '</span>' +
        '<a href="#" class="add-to-rack"><i class="icon-hanger"></i>add to rack</a></div>';
    }else{
      return '<div class="item"><a href="#" class="remove-from-rack" data-sku="' + 
        details.sku + '" data-idx="' + idx + '"><i class="fa fa-times"></i></a>' +
        '<div class="image"><img src="' + details.product_image_url + 
        '" style="width:50px"/></div><div class="details">' +
        '<span class="name">' + details.product_name + '</span>' +
        '<span class="avail">' + details.availability + '</span>' +
        merch + '' + manu + '' + price_display + 
        '<span class="size"><em>size</em>' + details.size + '</span></div></div>'
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
      q += 'text=' + text; 
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
          console.log(values)
          facets.push(
            '&' + qparam + '=' + values.join('|')
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