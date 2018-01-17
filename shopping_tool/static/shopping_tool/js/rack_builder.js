/**
* @description rack_builder namespace object, conatining the functionality and templates rack management
*/
var rack_builder = {
  /**
  * @description cache array of stylist's favorites, updated at load
  */
  favorites: [],
  /**
  * @description cache array of favorited product ids, used to set correct favorite link 
  */
  favorites_product_ids: [],   
  /** 
  * @description cache of styling session
  */
  session_id: '',
  /** 
  * @description adding an item to stylists favorites list
  * @param {DOM Object} link - item link being added to favorites
  */
  addFavorite: function(link){
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
          $('#fave-prods').find('div.item[data-fave="' + fave + '"]').remove();
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
          rack_builder.favorites.push(response);
          rack_builder.favorites_product_ids.push(response.product);
          link.data('faveid', response.id).addClass('favorited').find('i').removeClass('fa-heart-o').addClass('fa-heart');
          $('#fave-prods').append(rack_builder.favoriteTemplate(link.data('details')))
        },
        type: 'PUT',
        url: '/shopping_tool_api/user_product_favorite/0/'
      }); 
    }   
  },
  /**
  * @description add to rack functionality
  * @param {DOM object} item - link clicked
  * @param {string} page - which page the add to rack call initiated 
  * @param {boolean} from_compare - if inpsect initiation came from compare looks list
  */
  addToRack: function(item, page, from_compare){
    var rack = $('#rack-list');
    var existing = rack.data('skus');
    var details = item.data('details');
    var idx = item.closest('div.item').index();
    var items = rack.find('div.item').length;
    var sku = details.id + '_' + details.merchant_id + '_' + details.product_id + '_' + details.sku;
    var add_to_list = false;
    if(existing == undefined){
      if(page == 'search'){
        item.addClass('selected').html('<i class="fa fa-check"></i> added to rack');
      }else if(page == 'inspect'){
        item.addClass('selected').html('<i class="fa fa-check"></i> racked');
      }
      rack.data('skus', details.sku);
      add_to_list = true;
    }else{
      existing = existing.split(',');
      if(existing.indexOf(sku) == -1){
        existing.push(sku);
        rack.data('skus', existing.join(','));
        if(page == 'search'){
          item.addClass('selected').html('<i class="fa fa-check"></i> added to rack');
        }else if(page == 'inspect'){
          item.addClass('selected').html('<i class="fa fa-check"></i> racked');
        }
        add_to_list = true;
      }
    }
    if(add_to_list == true){
      if(items == 0){rack.html('<a class="close-all-rack-sections" href="#"><i class="fa fa-caret-square-o-up"></i>collapse all sections</a>')}
      var obj = {
        product: parseInt(details.id),
        allume_styling_session: parseInt(rack_builder.session_id)
      }
      $.ajax({
        contentType : 'application/json',
        data: JSON.stringify(obj),
        success:function(response){
          var itm = rack_builder.itemTemplate(details, 'rack', idx, response.id);
          var categories = [];
          var sanitized_cat = details.primary_category.replace('&amp;', 'and').replace(/&#(\d+);/g, function(match, match2) {return String.fromCharCode(+match2);});
          $.each(rack.find('div.block'), function(idx){
            categories.push($(this).data('category'));
          });
          if(categories.indexOf(sanitized_cat) == -1){
            categories.push(sanitized_cat);
            categories.sort();
            var rackidx = categories.indexOf(sanitized_cat);
            var new_category = '<a href="#" class="rack-section-toggle"><i class="fa fa-angle-down"></i>' + 
              details.primary_category + '</a><div class="block" data-category="' + sanitized_cat + 
              '"></div>';
            if(rackidx == 0){
              rack.find('.close-all-rack-sections').after(new_category);
            }else if(rackidx == (categories.length -1)){
              rack.append(new_category);
            }else{
              rack.find('div.block').eq((rackidx -1)).after(new_category);
            }
          }
          rack.find('div.block[data-category="' + sanitized_cat + '"]').append(itm)
          rack_builder.updateRackCount();
          if(from_compare == true){
            look_builder.orderedRack();
          }
        },
        type: 'PUT',
        url: '/shopping_tool_api/rack_item/0/'
      });
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
  * @desscription favorite item template
  * @param {object} obj - item fields in json format
  * @returns {string} HTML of favorite item
  */
  favoriteTemplate: function(obj){
    var fave_idx = rack_builder.favorites_product_ids.indexOf(obj.id);
    var favorite_object = rack_builder.favorites[fave_idx];
    var fave_link = '<span class="favorited" data-productid="' + 
      obj.id + '" data-faveid="' + favorite_object.id + '"><i class="fa fa-heart"></i></span>';
         
    var retail = obj.retail_price;
    var sale = obj.sale_price;
    var price_display = '';   
    if((sale >= retail)||(sale == 0)){
      price_display = '<span class="price">' + numeral(retail).format('$0,0.00') + '</span>';
    }else{
      price_display = '<span class="price"><em>(' + numeral(retail).format('$0,0.00') + 
        ')</em>' + numeral(sale).format('$0,0.00') + '</span>';
    }      
    var itm = '<div class="item" data-productid="' + obj.id + '" title="' + obj.merchant_name + ' by ' + 
    obj.manufacturer_name + '" data-fave="' + favorite_object.id  + '"><a href="#" ' +
    'data-productid="' + obj.id + '" data-name="' + obj.product_name + '" data-brand="' + 
    obj.manufacturer_name + '" class="fave-object">' + fave_link + '<div class="image"><img src="' + obj.product_image_url + 
    '"/></div><div class="details">' + price_display + '</div></a></div>';
    return itm;
  },
  /**
  * @description build out the rack looks panel
  * @param {string} type - query type
  * @param {string} id - DOM id string
  */
  getRackLooks: function(type, id){
    var lookup = {
        "client": parseInt($('#user-clip').data('userid')),
        "allume_styling_session": rack_builder.session_id,
        "stylist": parseInt($('#stylist').data('stylistid')),
        "page": 1
      }
    if(type == 'favorites'){
      lookup.favorites_only = "True";
      delete lookup.client;
      delete lookup.allume_styling_session;
      delete lookup.stylist;
    }
    $.ajax({
      contentType : 'application/json',
      data: JSON.stringify(lookup),
      success:function(response){
        var markup = [];
        var cropped_images = [];
        for(var i = 0, l = response.looks.length; i<l; i++){
          var comp = response.looks[i];
          var look_products_markup = ['<div class="rack-look-wrapper"><div class="rack-looks-layout">'];
          for(var ix = 0, lx = comp.look_layout.layout_json.length; ix<lx; ix++){
            var block = comp.look_layout.layout_json[ix];
            var position = block.position;
            var product_markup = [];
            for(var p = 0, prods = comp.look_products.length; p<prods; p++){
              var prod = comp.look_products[p];
              if(prod.layout_position == position){
                var src = prod.product.product_image_url;
                if(prod.cropped_dimensions != null){
                  var crop = {
                    id: type + 'racklook-' + comp.id + '-item-' + prod.id,
                    src: look_proxy + '' + src,
                    dims: prod.cropped_dimensions
                  }
                  cropped_images.push(crop);
                }
                product_markup.push(
                  '<div class="item"><a href="#" class="item-detail" ' + 
                    'data-name="' + prod.product.product_name + '" data-brand="' + prod.product.manufacturer_name + 
                    '" data-productid="' + prod.product.id + '"><span id="' + type + 'racklook-' + comp.id + '-item-' + prod.id + 
                    '"><img style="height:' + block.height + 'px" src="' + src + '"/></span></a></div>'
                );
              }
            }
            look_products_markup.push(
              '<div class="layout-block" style="height:' + (block.height - 4) + 'px;' +
              'width:' + (block.width - 4) + 'px;top:' + block.y + 'px;left:' + block.x + 
              'px" data-position="' + position + '">' + product_markup.join() + '</div>'
            );
          }
          look_products_markup.push('</div></div>');
          markup.push(
            '<div class="rack-look"><a href="#" class="look-link" data-lookid="' + comp.id + '" data-lookname="' +
            comp.name + '" data-lookdesc="' + comp.description + '" data-looklayoutid="' + comp.look_layout.id + 
            '">edit look</a><h3>' + comp.name + '</h3><span class="layout"><em>layout: </em>' + 
            comp.look_layout.display_name + '</span><div class="rack-look-display">' + 
            look_products_markup.join('') + '</div><span class="layout desc"><em>description: </em>' + 
            comp.description + '</span></div>'
          );
        }
        if(markup.length == 0){ 
          $(id).html('<div class="empty">Add looks to your rack...</div>')
        }else if(markup.length > 0){
          $(id).html(markup.join(''));
          /* afix cropped images if present */
          if(cropped_images.length > 0){
            for(var i = 0, l = cropped_images.length; i<l; i++){
              look_builder.getCroppedImage(cropped_images[i], id);
            }
          }
        }
      },
      type: 'POST',
      url: '/shopping_tool_api/look_list/'
    });
  },
  /**
  * @description init function of rack builder, created functionality and markup
  */
  init: function(){
    /* cache the session id */
    rack_builder.session_id = $('body').data('stylesession');
    /* set initital rack products */
    var rack_list = $('#rack-list');
    initial_rack.sort(function(a,b){
      if(a.primary_category.toLowerCase() > b.primary_category.toLowerCase()){ return 1}
      if(a.primary_category.toLowerCase() < b.primary_category.toLowerCase()){ return -1}
      return 0;
    });
    if(initial_rack.length > 0){
      var plural = initial_rack.length == 1 ? 'item' : 'items' ;
      rack_list.append(
        '<span id="rack-number">' + initial_rack.length + ' ' + plural + '</span>' +
        '<a class="close-all-rack-sections" href="#"><i class="fa fa-caret-square-o-up"></i>collapse all sections</a>'
      )
    }
    for(var i = 0, l = initial_rack.length; i<l; i++){
      var obj = initial_rack[i];
      var itm = rack_builder.itemTemplate(obj, 'rack', '', obj.rack_id);
      var sanitized_cat = obj.primary_category.replace('&amp;', 'and').replace(/&#(\d+);/g, function(match, match2) {return String.fromCharCode(+match2);});
      var category_exists = rack_list.find('div.block[data-category="' + sanitized_cat + '"]').length;
      if(category_exists == 0){
        rack_list.append(
          '<a href="#" class="rack-section-toggle"><i class="fa fa-angle-down"></i>' + 
          obj.primary_category + '</a><div class="block" data-category="' + sanitized_cat + 
          '"></div>'
        );
      }
      rack_list.find('div.block[data-category="' + sanitized_cat + '"]').append(itm);
    }
    var existing_items = []
    $.each(rack_list.find('a.remove-from-rack'), function(idx){
      existing_items.push($(this).data('sku'));
    });
    rack_list.data('skus', existing_items.join(','));
    /* create favorites section and add functionality */
    if(stylist_favorites.length > 0){
      var fave_prods = $('#fave-prods');
      for(var i = 0, l = stylist_favorites.length; i<l; i++){
        var obj = stylist_favorites[i];
        var itm = rack_builder.favoriteTemplate(obj);
        fave_prods.append(itm);
      }
    }
    $('#rack-tabs a.tab').click(function(e){
      e.preventDefault();
      var link = $(this);
      var div = $(link.attr('href'));
      if(link.hasClass('on') == false){
        link.addClass('on').siblings('a').removeClass('on');
        div.addClass('show').siblings('div.rack-section').removeClass('show')
      }
    });
    $('#favorites-list').on('click','a.rack-section-toggle', function(e){
      e.preventDefault();
      var link = $(this);
      var i = link.find('i')
      var div = link.next('div.block')
      if(link.hasClass('closed')){
        link.removeClass('closed');
        i.removeClass('fa-angle-right').addClass('fa-angle-down');
        div.slideDown();
      }else{
        link.addClass('closed');
        i.removeClass('fa-angle-down').addClass('fa-angle-right');
        div.slideUp();       
      }
    }).on('click', 'a.fave-object', function(e){
      e.preventDefault();
      var target = $(e.target);
      var link = $(this);
      if(target.hasClass('fa')){
        var fave = target.closest('span').data('faveid');
        var product_id = target.closest('span').data('productid');
        var index = rack_builder.favorites_product_ids.indexOf(product_id);
        rack_builder.favorites_product_ids.splice(index, 1);
        rack_builder.favorites.splice(index, 1);
        $.ajax({
          contentType : 'application/json',
          error: function(response){
            console.log(response);
          },
          success:function(response){
            var result_links = $('#results a.favorited');
            if(result_links.length > 0){
              $.each(result_links, function(idx){
                var fav = $(this);
                var fav_id = fav.data('faveid');
                if(fav_id == fave){
                  fav.data('faveid','').removeClass('favorited').find('i')
                  .removeClass('fa-heart').addClass('fa-heart-o');
                }
              });
            }
            link.closest('.item').remove();
          },
          type: 'DELETE',
          url: '/shopping_tool_api/user_product_favorite/' + fave + '/'
        });
      }else{
        rack_builder.inspectItem(link);
      }       
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
    Mousetrap.bind('shift+z+x', function(e) {
      var rack = $('#rack');
      if(rack.hasClass('show')){
        rack.removeClass('show');
      }else{
        rack.addClass('show');
      }
      return false;
    });
    rack_list.on('click','a.close-all-rack-sections', function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('open-all') == false){
        link.addClass('open-all').html('<i class="fa fa-caret-square-o-down"></i>expand all sections');
        $.each(rack_list.find('a.rack-section-toggle'),function(idx){
          var link = $(this);
          var i = link.find('i')
          var div = link.next('div.block');
          if(link.hasClass('closed') == false){
            link.addClass('closed');
            i.removeClass('fa-angle-down').addClass('fa-angle-right');
            div.slideUp();
          }
        });        
      }else{
        link.removeClass('open-all').html('<i class="fa fa-caret-square-o-up"></i>collapse all sections');
        $.each(rack_list.find('a.rack-section-toggle'),function(idx){
          var link = $(this);
          var i = link.find('i')
          var div = link.next('div.block');
          if(link.hasClass('closed') == true){
            link.removeClass('closed');
            i.removeClass('fa-angle-right').addClass('fa-angle-down');
            div.slideDown();
          }
        });
      }
    }).on('click','a.remove-from-rack',function(e){
      e.preventDefault();
      var link = $(this);
      var sku = link.data('sku');
      var rack = $('#rack-list');
      var existing = rack.data('skus').split(',');
      var idx = existing.indexOf(sku);
      existing.splice(idx,1);
      rack.data('skus',existing.join(','));
      /* undo selected btn */
      if(link.data('idx') != ''){
        var list_entry = $('#results div.item').eq(link.data('idx'));
        var add_link = list_entry.find('a.add-to-rack');
        if(add_link.length > 0){
          var details = add_link.data('details')
          var link_sku = details.id + '_' + details.merchant_id + '_' + details.product_id + '_' + details.sku;
          if(link_sku == sku){
            add_link.html('<i class="icon-hanger"></i>add to rack').removeClass('selected');
          }  
        }
      }
      $.ajax({
        success:function(response){
          var parent_block = link.closest('div.block');
          link.closest('div.item').remove();
          if(parent_block.find('div.item').length == 0){
            parent_block.prev('a.rack-section-toggle').remove();
            parent_block.remove();
          }
          /* add user friendly markup if rack is empty */
          if(rack.find('div.item').length == 0){
            rack.html('<div class="empty">Add items to your rack...</div>');
          }
          rack_builder.updateRackCount();
        },
        type: 'DELETE',
        url: '/shopping_tool_api/rack_item/' + link.data('rackid') + '/'
      });
    }).on('click','a.rack-section-toggle', function(e){
      e.preventDefault();
      var link = $(this);
      var i = link.find('i')
      var div = link.next('div.block')
      if(link.hasClass('closed')){
        link.removeClass('closed');
        i.removeClass('fa-angle-right').addClass('fa-angle-down');
        div.slideDown();
      }else{
        link.addClass('closed');
        i.removeClass('fa-angle-down').addClass('fa-angle-right');
        div.slideUp();       
      }
    });
    /* inspect item functionality events */
    $('#inspect-item').on('click', 'a.close-inspect', function(e){
      e.preventDefault();
      $('#inspect-item').fadeOut();
    }).on('click','a.favorite',function(e){
      e.preventDefault();
      var link = $(this);
      rack_builder.addFavorite(link);
    }).on('click','a.add-to-rack',function(e){
      e.preventDefault();
      var link = $(this);
      var from_compare = link.hasClass('compare') ? true : false;
      rack_builder.addToRack(link, 'inspect', from_compare);
    });
    /* get all looks */
    rack_builder.getRackLooks('regular', '#looks-list');
    rack_builder.getRackLooks('favorites', '#fave-looks');

  },
  /**
  * @description inpect item functionality allows for clicking favorites or look items to view fuller details 
  *              and either rack of favorite any of the sizes associated with the clicked upon item
  * @param {DOM object} link - item link triggering the inspect
  * @param {string} view - option view flag to add additional processing if required
  */
  inspectItem: function(link, view){
    var view_class = view == undefined ? '' : view;
    var id = parseInt(link.data('productid'));
    $.ajax({
      beforeSend: function(){
        $('#inspect-item').html(
          '<div class="stage"><a href="#" class="close-inspect"><i class="fa fa-times"></i></a>' +
        '<div class="loader">' +
        '<span class="pulse_loader"></span>' +
        '<span class="pulse_message">Finding your requested item and all of its sizes...</span>' +
        '</div></div>'
        ).fadeIn();
      },
      type: "GET",
      url: '/product_api/get_product/' + id,
      success: function(results){
        var sizes_list = [];
        var markup = [];
        results.data.sort(function(a,b){
          var a_size = isNaN(a._source.size) ? a._source.size : parseInt(a._source.size);
          var b_size = isNaN(b._source.size) ? b._source.size : parseInt(b._source.size);
          if(a_size > b_size){ return 1; }
          if(a_size < b_size){ return -1; }
          return 0;          
        })
        for(var i = 0, l = results.data.length; i<l; i++){
          var product = results.data[i]._source;
          var fave_link = '<a href="#" class="favorite" data-productid="' + 
            product.id + '"><i class="fa fa-heart-o"></i></a>';
          var fave_idx = rack_builder.favorites_product_ids.indexOf(product.id);
          if(fave_idx > -1){
            var favorite_object = rack_builder.favorites[fave_idx];
            fave_link = '<a href="#" class="favorite favorited" data-productid="' + 
            product.id + '" data-faveid="' + favorite_object.id + '"><i class="fa fa-heart"></i></a>';
          }
          var rack_link = '<a href="#" class="add-to-rack ' + view_class + 
              '" data-productid="' + product.id + '"><i class="icon-hanger"></i>add to rack</a>';          
          if(product.id == id){
            var retail = product.retail_price;
            var sale = product.sale_price;
            var price_display = '';
            var merch = '<span class="merch">' + product.merchant_name + '</span>';
            var manu = '<span class="manu">by ' + product.manufacturer_name + '</span>';  
            if((sale >= retail)||(sale == 0)){
              price_display = '<span class="price">' + numeral(retail).format('$0,0.00') + '</span>';
            }else{
              price_display = '<span class="price"><em>(' + numeral(retail).format('$0,0.00') + 
                ')</em>' + numeral(sale).format('$0,0.00') + '</span>';
            }
            if(product.merchant_name == undefined || product.merchant_name == ''){ merch = ''; }
            if(product.manufacturer_name == undefined || product.manufacturer_name == ''){ manu = ''; }   
            markup.push(
              '<div class="stage"><a href="#" class="close-inspect"><i class="fa fa-times"></i></a>' +
              '<h2>' + product.product_name + '</h2><div class="inspect-overflow"><table>' +
              '<tr><td class="img" rowspan="2"><img src="' + product.product_image_url + '"/>' + 
              fave_link + '' + rack_link + '</td>' +
              '<td class="details"><a href="' + product.product_url + '" target="_blank" class="name">' + 
              product.product_name + '</a>' +  merch + '' + manu + '<p class="item-desc"> '+ 
              product.short_product_description + '</p>' + price_display +
              '<span class="general"><em>size:</em>' + product.size + '</span>' +
              '<span class="general"><em>sku:</em>' + product.sku + '</span>' +
              '<span class="general"><em>color:</em>' + product.color + '</span>' +              
              '<span class="general"><em>category:</em>' + product.primary_category + 
              '</span></td></tr><tr><td id="inspect-sizes"><span class="general header"><em>other sizes:</em>' +
              '</span></td></table></div></div>'
            );
          }else{
            sizes_list.push(
              '<div class="inspect-alt-size"><table><tr><td class="size-img">' +
              '<img src="' + product.product_image_url + '"/></td><td>' +
              '<span class="general"><em>store:</em>' + product.merchant_name + '</span>' +
              '<span class="general"><em>size:</em>' + product.size + '</span>' +
              '<span class="general"><em>sku:</em>' + product.sku + '</span>' +
              '<span class="general"><em>color:</em>' + product.color + '</span>' +
              fave_link + '' + rack_link + '</td></tr></table></div>'
            )
          }
        }
        $('#inspect-item').html(markup.join(''));
        $('#inspect-sizes').append(sizes_list.join(''));
        /* add info to each link */
        for(var i = 0, l = results.data.length; i<l; i++){
          var obj = results.data[i];
          var rackit = $('#inspect-item').find('a.add-to-rack[data-productid="' + obj._source.id + '"]');
          var fave = $('#inspect-item').find('a.favorite[data-productid="' + obj._source.id + '"]');
          rackit.data('details',obj._source);
          fave.data('details',obj._source)
        }
      }
    });
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
    var retail = details.retail_price;
    var sale = details.sale_price;
    var price_display = '';   
    if((sale >= retail)||(sale == 0)){
      price_display = '<span class="price">' + numeral(retail).format('$0,0.00') + '</span>';
    }else{
      price_display = '<span class="price"><em>(' + numeral(retail).format('$0,0.00') + 
        ')</em>' + numeral(sale).format('$0,0.00') + '</span>';
    }
    return '<div class="item" data-productid="' + details.id + '" title="' + details.merchant_name + ' by ' + 
      details.manufacturer_name + '"><a href="#" class="remove-from-rack" data-sku="' + 
      details.id + '_' + details.merchant_id + '_' + details.product_id + '_' + details.sku + 
      '" data-idx="' + idx + '" data-productid="' + details.id + '" data-rackid="' + 
      rack_item_id + '"><i class="fa fa-times"></i></a>' +
      '<div class="image"><img src="' + details.product_image_url + 
      '"/></div><div class="details">' + price_display + '</div></div>';
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