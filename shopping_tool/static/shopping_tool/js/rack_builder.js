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
        allume_styling_session: parseInt(rack_builder.session_id)
      }
      $.ajax({
        contentType : 'application/json',
        data: JSON.stringify(obj),
        success:function(response){
          var itm = rack_builder.itemTemplate(details, 'rack', idx, response.id);
          var categories = [];
          $.each(rack.find('div.block'), function(idx){
            categories.push($(this).data('category'));
          });
          if(categories.indexOf(details.primary_category) == -1){
            categories.push(details.primary_category);
            categories.sort();
            var idx = categories.indexOf(details.primary_category);
            var new_category = '<a href="#" class="rack-section-toggle"><i class="fa fa-angle-down"></i>' + 
              details.primary_category + '</a><div class="block" data-category="' + details.primary_category + 
              '"></div>';
            if(idx == 0){
              rack.prepend(new_category);
            }else if(idx == (categories.length -1)){
              rack.append(new_category);
            }else{
              rack.find('div.block').eq((idx -1)).after(new_category);
            }
          }
          rack.find('div.block[data-category="' + details.primary_category + '"]').append(itm)
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
  init: function(){
    /* set initital rack products */
    var rack_list = $('#rack-list');
    initial_rack.sort(function(a,b){
      if(a.primary_category.toLowerCase() > b.primary_category.toLowerCase()){ return 1}
      if(a.primary_category.toLowerCase() < b.primary_category.toLowerCase()){ return -1}
      return 0;
    });
    for(var i = 0, l = initial_rack.length; i<l; i++){
      var obj = initial_rack[i];
      var itm = rack_builder.itemTemplate(obj, 'rack', '', obj.rack_id);
      var category_exists = rack_list.find('div.block[data-category="' + obj.primary_category + '"]').length;
      if(category_exists == 0){
        rack_list.append(
          '<a href="#" class="rack-section-toggle"><i class="fa fa-angle-down"></i>' + 
          obj.primary_category + '</a><div class="block" data-category="' + obj.primary_category + 
          '"></div>'
        );
      }
      rack_list.find('div.block[data-category="' + obj.primary_category + '"]').append(itm);
    }
    var existing_items = []
    $.each(rack_list.find('a.remove-from-rack'), function(idx){
      existing_items.push($(this).data('sku'));
    });
    rack_list.data('skus', existing_items.join(','));
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
    Mousetrap.bind('shift+q+w', function(e) {
      $('#new-look-error').html('');
      $('#new-look-name').val('');
      $('#new-look-layout')[0].selectize.setValue('',true);      
      $('#create-look').fadeToggle();
      return false;
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