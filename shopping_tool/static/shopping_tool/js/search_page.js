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
    utils.menu();
    utils.client();
    rack_builder.init();
    look_builder.functionality();
    /* cache the session id */
    search_page.session_id = $('body').data('stylesession');
    /* add keyboard shortcuts for client open/close */
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
      }else if(link.hasClass('remove-category')){
        $('#search-categories')[0].selectize.setValue('',true);
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
    $('#search-categories').val('').selectize({ create: false, sortField: 'text'});
    /* results functionality */
    $('#results').on('click','a.favorite',function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('favorited')){
        var fave = link.data('faveid');
        var product_id = link.data('productid');
        var index = rack_builder.favorites_product_ids.indexOf(product_id);
        rack_builder.favorites_product_ids.splice(index, 1);
        rack_builder.favorites.splice(index, 1);
        $.ajax({
          contentType : 'application/json',
          error: function(response){
            console.log(response);
          },
          success:function(response){
            console.log(response);
            $('#favorites-list').find('div.item[data-fave="' + fave + '"]').remove();
            link.data('faveid','').removeClass('favorited').find('i').removeClass('fa-heart').addClass('fa-heart-o');
          },
          type: 'DELETE',
          url: '/shopping_tool_api/user_product_favorite/' + fave + '/'
        }); 
      }else{
        var fave = {
          "stylist": parseInt($('#stylist').data('stylistid')) ,
          "product": parseInt(link.data('productid'))     
        }
        $.ajax({
          contentType : 'application/json',
          data: JSON.stringify(fave),
          error: function(response){
            console.log(response);
          },
          success:function(response){
            console.log(response);
            rack_builder.favorites.push(response);
            rack_builder.favorites_product_ids.push(response.product);
            link.data('faveid', response.id).addClass('favorited').find('i').removeClass('fa-heart-o').addClass('fa-heart');
            $('#favorites-list').append(rack_builder.favoriteTemplate(link.data('details')))
          },
          type: 'PUT',
          url: '/shopping_tool_api/user_product_favorite/0/'
        }); 
      }
    }).on('click','a.add-to-rack',function(e){
      e.preventDefault();
      var link = $(this);
      rack_builder.addToRack(link, 'search');
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
      //var buckets = Object.keys(facets);
      var display_order = ['_filter_size','_filter_price_range','_filter_brand',
                           '_filter_merchant_name','_filter_color','_filter_material'];
      for(var i = 0, l = display_order.length; i<l; i++){
        var bucket = display_order[i];
        console.log(bucket)
        var facet_list = facets[bucket];
        console.log(facet_list)
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
      //group_markup.names.sort();
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
  * @returns {string} HTML
  */   
  itemTemplate: function(details, view){
    var w = $('#results').width() / 3;   
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
    var fave_link = '<a href="#" class="favorite" data-productid="' + 
      details.id + '"><i class="fa fa-heart-o"></i></a>';
    var fave_idx = rack_builder.favorites_product_ids.indexOf(details.id);
    if(fave_idx > -1){
      var favorite_object = rack_builder.favorites[fave_idx];
      fave_link = '<a href="#" class="favorite favorited" data-productid="' + 
      details.id + '" data-faveid="' + favorite_object.id + '"><i class="fa fa-heart"></i></a>';
    }
    return '<div class="item"><div class="image">' + fave_link + '<img src="' + 
      details.product_image_url + '"></div><a href="' + details.product_url + 
      '" target="_blank" class="name">' + details.product_name + '</a>' + 
      '<a href="#" class="add-to-rack" data-productid="' + details.id + 
      '"><i class="icon-hanger"></i>add to rack</a>' + merch + 
      '' + manu + '<a href="#" class="info-toggle"><i class="fa fa-info-circle"></i></a>' + 
      price_display + '<div class="tt"><span><em>size:</em>' + 
      details.size + '</span><span><em>description:</em>' + details.short_product_description + 
      '</span></div></div>';
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
    var category = $('#search-categories').val();
    if(category != ''){
      facets.push('&primary_category=' + category);
      selection_markup.push(
        '<a href="#" class="remove-category" data-qparam="primary_category" ' +
        'data-facet="' + category + '">' + category + 
        '<i class="fa fa-times-circle"></i></a>'
      );      
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
    q += '&page=' + page + '' + facets.join('');
    //console.log('query string: ' + q)
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
          utils.pagerTemplate(results.page, results.total_items, results.num_per_page);
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
          var dom = items.eq(i)
          dom.find('a.add-to-rack').data('details',details);
          dom.find('a.favorite').data('details',details);     
        }
      }
      utils.equalHeight($('#results div.item'));
    }else{
      $('#results').html('<div class="no-results">There were no products matching your supplied criteria...</div>');
    }
  }
}