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
  * @description add to rack functionality
  * @param {DOM object} item - link clicked
  * @param {string} page - which page the add to rack call initiated 
  */
  addToRack: function(item, page){
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
        }
        add_to_list = true;
      }
    }
    if(add_to_list == true){
      if(items == 0){rack_list.html('<a class="close-all-rack-sections" href="#"><i class="fa fa-caret-square-o-up"></i>collapse all sections</a>')}
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
              rack.prepend(new_category);
            }else if(rackidx == (categories.length -1)){
              rack.append(new_category);
            }else{
              rack.find('div.block').eq((rackidx -1)).after(new_category);
            }
          }
          rack.find('div.block[data-category="' + sanitized_cat + '"]').append(itm)
          rack_builder.updateRackCount();
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
    var fave_link = '<a href="#" class="favorited" data-productid="' + 
      obj.id + '" data-faveid="' + favorite_object.id + '"><i class="fa fa-heart"></i></a>';
         
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
    obj.manufacturer_name + '" data-fave="' + favorite_object.id  + '">' + fave_link + 
    '<div class="image"><img src="' + obj.product_image_url + 
    '"/></div><div class="details">' + price_display + '</div></div>';
    return itm;
  } ,
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
      rack_list.append('<a class="close-all-rack-sections" href="#"><i class="fa fa-caret-square-o-up"></i>collapse all sections</a>')
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
    var fave_list = $('#favorites-list');
    for(var i = 0, l = stylist_favorites.length; i<l; i++){
      var obj = stylist_favorites[i];
      var itm = rack_builder.favoriteTemplate(obj);
      fave_list.append(itm);
    }    
    $('#favorites-toggle').click(function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('open')){
        link.removeClass('open').html('show my favorites')
      }else{
        link.addClass('open').html('hide my favorites')
      }
      fave_list.toggleClass('show');
    });
    fave_list.on('click', 'a.favorited', function(e){
      e.preventDefault();
      var link = $(this);
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
          var look_links = $('#all-looks-list a.favorited');
          if(look_links.length > 0){
            $.each(look_links, function(idx){
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
    });
    /* my rack functionality */
    $('#rack-toggle').click(function(e){
      e.preventDefault();
      $('#rack').toggleClass('show');
      $('#look-list').toggleClass('show');
    });
    $('#close-rack').click(function(e){
      e.preventDefault();
      $('#look-list').removeClass('show');
      $('#rack').delay(400)
      .queue(function (next) { 
        $(this).removeClass('show');
        next(); 
      });
    });
    Mousetrap.bind('shift+z+x', function(e) {
      var rack = $('#rack');
      if(rack.hasClass('show')){
        $('#look-list').removeClass('show');
        rack.delay(400)
        .queue(function (next) { 
          $(this).removeClass('show');
          next(); 
        });
      }else{
        rack.addClass('show');
        $('#look-list').addClass('show');
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