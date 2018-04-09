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
  * @description cache array of racked product ids, used to set correct add to rack link 
  */
  rack_product_ids: [],    
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
      if(fave != ''){
        link.data('faveid','').removeClass('favorited').find('i').removeClass('fa-heart').addClass('fa-heart-o');
        $('#fave-prods').find('div.item[data-fave="' + fave + '"]').remove();
        $.ajax({
          contentType : 'application/json',
          error: function(response){
            console.log(response);
          },
          success:function(response){
            console.log('removed favorite')
          },
          type: 'DELETE',
          url: '/shopping_tool_api/user_product_favorite/' + fave + '/'
        }); 
      }
    }else{
      var fave = {
        "stylist": parseInt($('#stylist').data('stylistid')) ,
        "product": parseInt(link.data('productid'))     
      }
      link.addClass('favorited').find('i').removeClass('fa-heart-o').addClass('fa-heart');
      $.ajax({
        contentType : 'application/json',
        data: JSON.stringify(fave),
        error: function(response){
          console.log(response);
        },
        success:function(response){
          rack_builder.favorites.push(response);
          rack_builder.favorites_product_ids.push(response.product);
          link.data('faveid', response.id);
          var obj = link.data('details')
          var fave_idx = rack_builder.favorites_product_ids.indexOf(obj.id);
          var favorite_object = rack_builder.favorites[fave_idx];
          var sold_out = obj.availability != 'in-stock' ? '<span class="sold-out">sold out</span>' : '';  
          var fave_item = '<div class="item" data-productid="' + obj.id + 
            '" data-productname="' + obj.product_name + 
            '" data-url="' + obj.product_image_url + 
            '" data-fave="' + favorite_object.id + 
            '" data-availability="' + obj.availability + '">' +
            '<img src="' + obj.product_image_url + '" class="handle"/>' +
            '<span class="badge"><i class="fa fa-heart"></i></span>' +
            '<a href="#"  class="view" data-productid="' + obj.id + 
            '"><i class="fa fa-align-left"></i></a><a href="#" class="remove-fave" data-productid="' + 
            obj.id + '" data-faveid="' + favorite_object.id + '"><i class="fa fa-times"></i></a>' + sold_out + '</div>'
          $('#fave-prods').prepend(fave_item);
          var fd = $('#fave-draggable');
          if(fd.length > 0){
            fd.prepend(fave_item);
          }
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
      item.addClass('selected').html('<i class="fa fa-check"></i> racked');
      rack.data('skus', sku);
      rack_builder.rack_product_ids.push(sku);
      add_to_list = true;
    }else{
      existing = existing.split(',');
      if(existing.indexOf(sku) == -1){
        existing.push(sku);
        rack_builder.rack_product_ids.push(sku);
        rack.data('skus', existing.join(','));
        item.addClass('selected').html('<i class="fa fa-check"></i> racked');
        add_to_list = true;
      }
    }
    if(add_to_list == true){
      var list_atr = $('#results').find('a.add-to-rack[data-productid="' + details.id + '"]')
      if((list_atr.length > 0)&&(list_atr.hasClass('selected') == false)){
        list_atr.addClass('selected').html('<i class="fa fa-check"></i> racked');
      }
      var obj = {
        product: parseInt(details.id),
        allume_styling_session: parseInt(rack_builder.session_id)
      }
      $.ajax({
        contentType : 'application/json',
        data: JSON.stringify(obj),
        error:function(response){
          console.log(response);
          alert("Sorry, we could not add this product to your rack at this time.")
          item.removeClass('selected').html('<i class="icon-hanger"></i> add to rack');
        },
        success:function(response){
          var new_rack_obj = { 
            "rack_id": response.id,
            "id": details.id,
            "added": moment().format("MM/DD/YYYY HH:mm"),
            "product_id": details.product_id,
            "sku": details.sku,
            "merchant_id": details.merchant_id,
            "merchant_name": details.merchant_name,
            "manufacturer_name": details.manufacturer_name,
            "product_name": details.product_name,
            "product_image_url": details.product_image_url,
            "primary_category": details.primary_category,
            "allume_category": details.allume_category,
            "current_price": details.current_price,
            "availability": details.availability
          }
          initial_rack.push(new_rack_obj);
          var sku = details.id + '_' + details.merchant_id + '_' + details.product_id + '_' + details.sku;
          var sold_out = details.availability != 'in-stock' ? '<span class="sold-out">sold out</span>' : '';
          $('#rack-list').prepend(
            '<div class="item" data-productid="' + details.id + 
            '" data-url="' + details.product_image_url + 
            '" data-productname="' + details.product_name + 
            '" data-sku="' + sku + 
            '" data-availability="' + details.availability + 
            '"><img class="handle" src="' + details.product_image_url + 
            '"/><a href="#"  class="view" data-productid="' + details.id + 
            '"><i class="fa fa-align-left"></i></a>' +
            '<a href="#" class="remove-from-rack" data-sku="' + sku + 
            '" data-rackid="' + response.id + '"><i class="fa fa-times"></i></a>' + sold_out + '</div>'
          );
          rack_builder.updateRackCount();
          if(from_compare == true){
            $('#rack-draggable div.look-builder-rack div.item:first').before(
              '<div class="item" data-productid="' + details.id + '" data-url="' + 
              details.product_image_url + '" data-sku="' + sku + '"' +
              ' data-availability="' + details.availability + 
              '"><img class="handle" src="' + details.product_image_url + 
              '"/><a href="#"  class="view" data-productid="' + details.id + 
              '"><i class="fa fa-align-left"></i></a><a href="#" class="remove" data-sku="' + 
              details.id + '_' + details.merchant_id + '_' + details.product_id + 
              '_' + details.sku + '" data-rackid="' + response.id + 
              '"><i class="fa fa-times"></i></a>' + sold_out + '</div>'
            );
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
    var price_display = '<span class="price">' + numeral(obj.current_price).format('$0,0.00') + '</span>';     
    var itm = '<div class="item" data-productid="' + obj.id + '" title="' + obj.merchant_name + ' by ' + 
    obj.manufacturer_name + '" data-productname="' + obj.product_name + 
    '" data-src="' + obj.product_image_url + '" data-fave="' + favorite_object.id  + '"><a href="#" ' +
    'data-productid="' + obj.id + '" data-name="' + obj.product_name + '" data-brand="' + 
    obj.manufacturer_name + '" class="fave-object">' + fave_link + 
    '<div class="image"><img src="' + obj.product_image_url + 
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
        "page": 1,
        "with_products": "False"
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
          var collage_img = '<div class="collage-placeholder">collage not yet created</div>';
          if(comp.collage != null){
            collage_img = '<a href="#" class="view-look-details" data-look="' + comp.id + 
            '"><img class="collage" src="' + comp.collage + '"/></a>';
          }
          markup.push(
            '<div class="rack-look"><a href="/look_builder/' + rack_builder.session_id + 
            '/?look=' + comp.id  + '" class="look-link">edit look</a><h3>' + comp.name + '</h3>' + 
            collage_img + '<span class="layout desc"><em>description: </em>' + 
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
    var rack_items = [];
    initial_rack.sort(function(a,b){
      if(a.added > b.added){ return -1}
      if(a.added < b.added){ return 1}
      return 0;      
    });
    for(var i = 0, l = initial_rack.length; i<l; i++){
      var data = initial_rack[i];
      var src = data.product_image_url;
      var sku = data.id + '_' + data.merchant_id + '_' + data.product_id + '_' + data.sku;
      var sold_out = data.availability != 'in-stock' ? '<span class="sold-out">sold out</span>' : '';
      rack_items.push(
        '<div class="item" data-productid="' + data.id + 
        '" data-productname="' + data.product_name + '" data-url="' + 
        src + '" data-sku="' + sku + '" data-availability="' + 
        data.availability + '"><img class="handle" src="' + src + 
        '"/><a href="#"  class="view" data-productid="' + data.id + 
        '"><i class="fa fa-align-left"></i></a>' +
        '<a href="#" class="remove-from-rack" data-sku="' + sku + 
        '" data-rackid="' + data.rack_id + 
        '"><i class="fa fa-times"></i></a>' + sold_out + '</div>'
      ); 
           
    }
    rack_list.html(rack_items.join(''))
    var existing_items = []
    $.each(rack_list.find('a.remove-from-rack'), function(idx){
      var sku = $(this).data('sku')
      existing_items.push(sku);
    });
    rack_list.data('skus', existing_items.join(','));
    /* create favorites section and add functionality */
    if(stylist_favorites.length > 0){

      stylist_favorites.sort(function(a,b){
        if(a.added > b.added){ return -1}
        if(a.added < b.added){ return 1}
        return 0;      
      });
      var fave_items = [];
      for(var i = 0, l = stylist_favorites.length; i<l; i++){
        var obj = stylist_favorites[i];
        var fave_idx = rack_builder.favorites_product_ids.indexOf(obj.id);
        var favorite_object = rack_builder.favorites[fave_idx];
        var sold_out = obj.availability != 'in-stock' ? '<span class="sold-out">sold out</span>' : '';        
        fave_items.push(
          '<div class="item" data-productid="' + obj.id + 
          '" data-productname="' + obj.product_name + 
          '" data-url="' + obj.product_image_url + 
          '" data-fave="' + favorite_object.id + 
          '" data-availability="' + obj.availability + '">' +
          '<img src="' + obj.product_image_url + '" class="handle"/>' +
          '<span class="badge"><i class="fa fa-heart"></i></span>' +
          '<a href="#"  class="view" data-productid="' + obj.id + 
          '"><i class="fa fa-align-left"></i></a><a href="#" class="remove-fave" data-productid="' + 
          obj.id + '" data-faveid="' + favorite_object.id + '"><i class="fa fa-times"></i></a>' +
          sold_out + '</div>'
        ); 
             
      }
      $('#fave-prods').html(fave_items.join(''));
      var fd = $('#fave-draggable');
      if(fd.length > 0){
        fd.html(fave_items.join(''));
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
    $('#favorites-list').on('click', 'a.view', function(e){
      e.preventDefault();
      var link = $(this);
      rack_builder.inspectItem(link, 'compare');
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
    }).on('click', 'a.remove-fave', function(e){
      e.preventDefault();
      var link = $(this);
      var fave = link.data('faveid');
      var product_id = link.data('productid');
      var index = rack_builder.favorites_product_ids.indexOf(product_id);
      rack_builder.favorites_product_ids.splice(index, 1);
      rack_builder.favorites.splice(index, 1);
      $.ajax({
        beforeSend:function(){
          link.closest('div.item').hide();
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
        },
        contentType : 'application/json',
        error: function(response){
          console.log(response);
        },
        success:function(response){
          link.closest('.item').remove();
        },
        type: 'DELETE',
        url: '/shopping_tool_api/user_product_favorite/' + fave + '/'
      });      
    }).on('click','a.view-look-details', function(e){
      e.preventDefault();
      var link = $(this);
      look_builder.lookDetails(link);
    });
    $('#looks-list').on('click','a.view-look-details', function(e){
      e.preventDefault();
      var link = $(this);
      look_builder.lookDetails(link);
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
    rack_list.on('click','a.remove-from-rack',function(e){
      e.preventDefault();
      var link = $(this);
      var sku = link.data('sku');
      var rack = $('#rack-list');
      var existing = rack.data('skus').split(',');
      var idx = existing.indexOf(sku);
      var arr_idx = rack_builder.rack_product_ids.indexOf(sku)
      existing.splice(idx,1);
      rack_builder.rack_product_ids.splice(arr_idx,1);
      rack.data('skus',existing.join(','));
      /* undo selected btn */
      $.each($('#results a.add-to-rack.selected'), function(link_idx){
        var rack_btn = $(this);
        var details = rack_btn.data('details')
        var link_sku = details.id + '_' + details.merchant_id + '_' + details.product_id + '_' + details.sku;
        if(link_sku == sku){
          rack_btn.html('<i class="icon-hanger"></i>add to rack').removeClass('selected');
        } 
      });
      $.ajax({
        beforeSend:function(){
          link.closest('div.item').hide();
        },
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
    }).on('click', 'a.view', function(e){
      e.preventDefault();
      var link = $(this);
      console.log(link.data())
      rack_builder.inspectItem(link, 'compare');
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
      if(link.hasClass('selected') == false){
        var from_compare = false;
        if(document.location.href.indexOf('look_builder') > -1){
          from_compare = true;
        }
        rack_builder.addToRack(link, 'inspect', from_compare);
      }
    }).on('click', 'a#color-toggle', function(e){
      e.preventDefault();
      var link = $(this);
      var pos = link.position()
      link.toggleClass('on')
      $('#color-options').css({left: pos.left + 1, top: pos.top + 30}).fadeToggle();
    }).on('click', 'a.size-by-color', function(e){
      e.preventDefault();
      var link = $(this);
      var color_link = $('#color-toggle');
      var data = color_link.data();
      var color = link.data('color');
      var sizes_list = [...new Set(data.colormap[color])].filter(String);
      var matching = {};
      var price_display = '';
      var fave_link = '';
      var rack_link = ''
      for(var i = 0, l = data.details.length; i<l; i++){
        var option = data.details[i];
        if(option._source.merchant_color.toLowerCase() == color){
          matching = option;
          price_display = '<em class="label">price:</em>' + numeral(matching._source.current_price).format('$0,0.00');
          fave_link = '<a href="#" class="favorite" data-productid="' + 
            matching._source.id + '"><i class="fa fa-heart-o"></i></a>';
          var fave_idx = rack_builder.favorites_product_ids.indexOf(matching._source.id);
          if(fave_idx > -1){
            var favorite_object = rack_builder.favorites[fave_idx];
            fave_link = '<a href="#" class="favorite favorited" data-productid="' + 
            matching._source.id + '" data-faveid="' + favorite_object.id + '"><i class="fa fa-heart"></i></a>';
          }
          rack_link = '<a href="#" class="add-to-rack" data-productid="' + 
            matching._source.product_id + '"><i class="icon-hanger"></i>add to rack</a>';
          var rack_sku = matching._source.id + '_' + matching._source.merchant_id + '_' + matching._source.product_id + '_' + matching._source.sku;
          var rack_idx = rack_builder.rack_product_ids.indexOf(rack_sku);
          if(rack_idx > -1){
            rack_link = '<a href="#" class="add-to-rack selected" data-productid="' + 
              matching._source.product_id + '"><i class="fa fa-check"></i> racked</a>';
          }
          break;
        }
      }
      color_link.removeClass('on').html(color + '<i class="fa fa-caret-down"></i>');
      link.addClass('selected').siblings('a').removeClass('selected');
      $('#sizes-list').html(sizes_list.join(', '));
      /* change the display to match new selection */
      if(matching._source != undefined){
        $('#inspected-item-img').attr('src', matching._source.product_image_url);
        var ii = $('#inspect-item')
        ii.find('a.favorite').remove();
        ii.find('a.add-to-rack').remove();
        ii.find('a.link-to-store').attr('href', matching._source.product_url).before(rack_link);
        ii.find('a.add-to-rack').data('details', matching._source).before(fave_link);
        ii.find('a.favorite').data('details', matching._source);
        if(price_display != ''){ $('#inspected-item-price').html(price_display); }
        $('#inspected-item-sku').html('<em>sku:</em>' + matching._source.sku)
      }
      $('#color-options').hide();
    })
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
        '<span class="pulse_message">Finding your requested item...</span>' +
        '</div></div>'
        ).fadeIn();
      },
      type: "GET",
      url: '/product_api/get_product/' + id + '/',
      error: function(){
        $('#inspect-item').html(
          '<div class="stage"><a href="#" class="close-inspect">' +
          '<i class="fa fa-times"></i></a><h2>could not find product...</h2>' +
          '<div class="lookup-error-msg">Please copy and paste the information below and send to ' +
          'Pamela Nguesseu <pamela@allume.co>:' +
          '<span class="msg"><strong>/product_api/get_product/ Error</strong>Product ' + id + ' failed to load ' +
          'at:<br/> ' +  moment().format('MM/DD/YYYY - HH:mm a') + '</span>Thank you.<br/>The Allume team</div></div>'
        );
      },
      success: function(results){
        console.log(results)
        var inspect = $('#inspect-item');
        var markup = [];
        var matching;
        var colors_hash = {color_names: [], color_sizes: {}};
        for(var i = 0, l = results.data.length; i<l; i++){
          var product = results.data[i]._source;
          var product_color = product.merchant_color.toLowerCase();
          if(colors_hash.color_names.indexOf(product_color) == -1){
            colors_hash.color_names.push(product_color)
            colors_hash.color_sizes[product_color] = [];
          }
          colors_hash.color_sizes[product_color] = colors_hash.color_sizes[product_color].concat(product.size.split(','));
          if(product.id == id){
            matching = product;
          }
        }
        colors_hash.color_names.sort();
        var product = matching;
        if(product != undefined){
          var color_options = [];
          var color_link = '';
          var sizes = '';
          for(var i = 0, l = colors_hash.color_names.length; i<l; i++){
            var color = colors_hash.color_names[i];
            if(color == product.merchant_color.toLowerCase()){
              if(l > 1){
                color_link = '<a href="#" id="color-toggle">' + color + '<i class="fa fa-caret-down"></i></a>'
              }else{
                color_link = color;
              }
              color_options.push('<a href="#" class="size-by-color selected" data-color="' + color + '">' + color + '</a>');
              var sizes_list = [...new Set(colors_hash.color_sizes[color])].filter(String);
              sizes = '<span id="sizes-list">' + sizes_list.join(', ') + '</span>';
            }else{
              color_options.push('<a href="#" class="size-by-color" data-color="' + color + '">' + color + '</a>');
            }
          }
          var fave_link = '<a href="#" class="favorite" data-productid="' + 
            product.id + '"><i class="fa fa-heart-o"></i></a>';
          var fave_idx = rack_builder.favorites_product_ids.indexOf(product.id);
          if(fave_idx > -1){
            var favorite_object = rack_builder.favorites[fave_idx];
            fave_link = '<a href="#" class="favorite favorited" data-productid="' + 
            product.id + '" data-faveid="' + favorite_object.id + '"><i class="fa fa-heart"></i></a>';
          }
          var rack_link = '<a href="#" class="add-to-rack" data-productid="' + 
            product.id + '"><i class="icon-hanger"></i>add to rack</a>';
          var rack_sku = product.id + '_' + product.merchant_id + '_' + product.product_id + '_' + product.sku;
          var rack_idx = rack_builder.rack_product_ids.indexOf(rack_sku);
          if(rack_idx > -1){
            rack_link = '<a href="#" class="add-to-rack selected" data-productid="' + 
              product.id + '"><i class="fa fa-check"></i> racked</a>';
          }
          var price_display = '<span class="price" id="inspected-item-price"><em class="label">price:</em>' + numeral(product.current_price).format('$0,0.00') + '</span>';
          var merch = '<span class="merch">' + product.merchant_name + '</span>';
          var manu = '<span class="manu">by ' + product.manufacturer_name + '</span>';  
          if(product.merchant_name == undefined || product.merchant_name == ''){ merch = ''; }
          if(product.manufacturer_name == undefined || product.manufacturer_name == ''){ manu = ''; }  
          var options_header = '';
          var options_class = '';
          if(color_options.length > 4){
            options_class = 'with-header'
            options_header = '<h6>' + (color_options.length - 1) + ' other color options</h6>';
          }  
          markup.push(
            '<div class="stage"><a href="#" class="close-inspect"><i class="fa fa-times"></i></a>' +
            '<h2>' + product.product_name + '</h2><div class="inspect-overflow"><table>' +
            '<tr><td class="img" rowspan="2"><img id="inspected-item-img" src="' + product.product_image_url + '"/>' + 
            fave_link + '' + rack_link + '<a href="' + product.product_url + '" target="_blank" class="link-to-store">' + 
            '<i class="fa fa-tag"></i>view at store</a></td><td class="details"><h4 class="name">' + product.product_name + '</h4>' + 
            merch + '' + manu + '<p class="item-desc"> '+ 
            product.short_product_description + '</p>' + price_display +
            '<span class="general" id="inspected-item-sku"><em>sku:</em>' + product.sku + '</span>' +
            '<span class="general"><em>colors:</em>' + color_link + '</span>' + 
            '<div id="color-options" class="' + options_class + '">' + options_header + 
            '<div>' + color_options.join('') + '</div></div>' +
            '<span class="general"><em>sizes:</em>' + sizes + '</span>' +             
            '<span class="general"><em>category:</em>' + product.allume_category  + 
            '</span><span class="general"><em>availability:</em>' + product.availability  + 
            '</span></td></tr></table><span class="shopping-for">styling for:</span>' + 
            $('#client-details-template').html() + '</div></div>'
          );
          inspect.html(markup.join(''));
          /* add info to each link */
          inspect.find('a.add-to-rack').data('details', product);
          inspect.find('a.favorite').data('details', product);
          inspect.find('a#color-toggle').data('colormap', colors_hash.color_sizes).data('details', results.data);
        }else{
          inspect.html(
            '<div class="stage"><a href="#" class="close-inspect">' +
            '<i class="fa fa-times"></i></a><h2>could not find product...</h2>' +
            '<div class="lookup-error-msg">Please copy and paste the information below and send to ' +
            'Pamela Nguesseu &lt;pamela@allume.co&gt;:' +
            '<span class="msg"><strong>/product_api/get_product/ Error</strong>Product ' + id + ' failed to return a viable product ' +
            'at:<br/>' +  moment().format('MM/DD/YYYY - HH:mm a') + '</span>Thank you.<br/>The Allume team</div></div>'
          );
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
    var price_display = '<span class="price">' + numeral(details.current_price).format('$0,0.00') + '</span>';
    var sku = details.id + '_' + details.merchant_id + '_' + details.product_id + '_' + details.sku;
    return '<div class="item" data-productid="' + details.id + '" title="' + details.merchant_name + ' by ' + 
      details.manufacturer_name + '" data-productname="' + details.product_name + '" data-sku="' + sku + 
      '" data-rackid="' + details.rack_id + '" data-src="' + details.product_image_url + 
      '"><a href="#" class="remove-from-rack" data-sku="' + sku + 
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