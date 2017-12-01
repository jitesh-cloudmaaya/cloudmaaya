/**
* @description look builder name space containing functionality for create look UI/ux for building looks
*/
var look_builder = {
  /**
  * @description look builder ui/ux functionality
  */
  functionality: function(){
    $('#close-design-look').click(function(e){
      e.preventDefault();
      $('#design-look').addClass('hide');
      $('#rack-draggable').html('');
      $('#look-drop').html('');
      $('#compare-looks').html('');
    });
    $('#rack-draggable').on('click','a.rack-section-toggle', function(e){
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
    $('#look-drop').on('click','a.look-more-details', function(e){
      e.preventDefault();
      var link = $(this);
      $('#look-indepth').html('').fadeIn();
      $.get('/shopping_tool_api/look/' + link.data('look') + '/', function(result){
        var markup = ['<table>'];
        result.look_products.sort(function(a,b){
          if(a.layout_position > b.layout_position){ return 1}
          if(a.layout_position < b.layout_position){ return -1}
          return 0;
        });
        for(var i = 0, l = result.look_products.length; i<l; i++){
          var prod = result.look_products[i];
          var retail = prod.product.retail_price;
          var sale = prod.product.sale_price;
          var price_display = '';
          var merch = '<span class="merch">' + prod.product.merchant_name + '</span>';
          var manu = '<span class="manu">by ' + prod.product.manufacturer_name + '</span>';    
          if((sale >= retail)||(sale == 0)){
            price_display = '<span class="price"><em class="label">price:</em>' + 
              numeral(retail).format('$0,0.00') + '</span>';
          }else{
            price_display = '<span class="price"><em class="label">price:</em><em class="sale">(' + 
              numeral(retail).format('$0,0.00') + ')</em>' + numeral(sale).format('$0,0.00') + '</span>';
          }
          markup.push(
            '<tr><td class="img"><img src="' + prod.product.product_image_url + '"/></td>' +
            '<td class="details"><a href="' + prod.product.product_url + '" target="_blank" class="name">' + 
            prod.product.product_name + '</a>' +  merch + '' + manu + '<p class="item-desc"> '+ 
            prod.product.short_product_description + '</p>' + price_display +
            '<span class="general"><em>size:</em>' + prod.product.size + '</span>' +
            '<span class="general"><em>category:</em>' + prod.product.primary_category + '</span></td></tr>'
          );
        }
        markup.push('</table>');
        $('#look-indepth').html(
          '<div class="stage"><a href="#" class="close-indepth"><i class="fa fa-times"></i></a>' +
          '<h2>' + result.name + '</h2><p class="layout"><em>layout: </em>' + result.look_layout.display_name + 
          '</p><div class="products">' + markup.join('') + '</div></div>'
        );
      });
    });
    $('#look-indepth').on('click', 'a.close-indepth', function(e){
      e.preventDefault();
      $('#look-indepth').fadeOut();
    })
  },
  /**
  * @description build new look link for drawer in rack
  * @param {object} data - the newly created look object
  */
  newLookLink: function(data){
    var layout_name = ''
    for(var i = 0, l = look_layouts.length; i<l; i++){
      var layout = look_layouts[i];
      if(layout.id == data.look_layout){
        layout_name = layout.name;
        break;
      }
    }
    $('#look-links').prepend(
      '<a href="#" class="look-link" data-lookid="' + data.id + '" data-lookname="' + data.name + '">' +
      '<table><tr><td class="icon"><i class="fa fa-shopping-bag"></i></td>' +
      '<td><span class="name">' + data.name + '</span>' +
      '<span class="layout"><em>layout:</em> ' + layout_name + 
      '</span></td></tr></table></a>' 
    );
  },
  /**
  * @description set up the builder ui/ux from clicked look link
  * @param {integer} id -  the look id 
  */
  setUpBuilder: function(id){
    /* get the look settings to build the drop zone */
    $.get('/shopping_tool_api/look/' + id + '/', function(result){
      var look_drop = $('#look-drop');
      var markup = [];
      for(var i = 0; i<result.look_layout.columns; i++){
        var col = ['<div class="column" id="lookdropcol' + i + '">'];
        var heights = result.look_layout.row_heights.split(',');
        for(var j = 0; j<result.look_layout.rows; j++){
          var h = heights[j];
          var position = i > 0 ? (j + 1) + result.look_layout.rows : j + 1 ;
          var product_markup = [];
          /* check if a look product has the same position as the newlay added row */
          for(var p = 0, prods = result.look_products.length; p<prods; p++){
            var prod = result.look_products[p];
            if(prod.layout_position == position){
              product_markup.push(
                '<div class="item" data-productid="' + prod.product.id + 
                '" data-lookitemid="' + prod.id + '">' +
                '<img class="handle" src="' + prod.product.product_image_url + 
                '"/></div>'
              );
            }
          }
          col.push(
            '<div class="row" style="height:calc(' + h + '% - 6px)">' + 
            product_markup.join('') + '</div>'
          );
        }
        col.push('</div>');
        markup.push(col.join(''));
      }
      /* add the created look markup to the ui, including instructions and trash bin */
      look_drop.html(
        '<div class="instructions"><div id="look-trash"></div>' +
        'Drag rack items from the left into open spots within the look layout.' +
        '<br/><br/>Dragging an item into an occupied spot will remove the old item ' +
        'from that position.<br/><br/>Drag items to trash to remove from the look.<br/><br/>' + 
        'Compare to other looks for the client to the right.<br/><br/>' +
        '<a href="#" class="look-more-details" data-look="' + id + '">' +
        '<i class="fa fa-search"></i>look details</a>' + 
        '</div><div class="drop-zone">' + markup.join('') + '</div>'
      );
      /* set nicer margins for drop box columns inside the look drop div */
      var col_widths = 0;
      $.each(look_drop.find('div.column'), function(idx){ col_widths += $(this).outerWidth(); });
      look_drop.find('div.column:first-child').css('marginLeft', ((look_drop.width() * 0.75) - col_widths)/2);
      /* add the trash functionality - simply accept objects and immediately remove from ui */
      new Sortable(document.getElementById('look-trash'), {
        group: "look",
        onAdd: function (evt) {
          var el = evt.item;
          el.parentNode.removeChild(el);
        }
      });
      /* add the drag/drop functionality to the newly created drop zones */
      $.each(look_drop.find('div.column div.row'), function(idx){
        var box = $(this)[0];
        new Sortable(box, {
          handle: ".handle",
          group: { name: "look", pull: true, put: true },
          sort: false,
          draggable: ".item",
          onAdd: function (evt) {
            var el = evt.item;
            var el_id = el.dataset.productid;
            var list = el.parentNode; 
            var parent_element = list.parentNode;
            var position = Array.prototype.indexOf.call(parent_element.children, list) + 1;
            /* create REST object */
            var obj = {
              layout_position: position,
              look: id,
              product: parseInt(el_id)              
            }
            /* create new look item in db */
            $.ajax({
              contentType : 'application/json',
              data: JSON.stringify(obj),
              success:function(response){
                /* assign the look item id to the element */
                el.setAttribute('data-lookitemid', response.id);
                if(list.children.length > 1){
                  var match_count = 0;
                  for(var i = 0, l = list.children.length; i<l; i++){
                    var child = list.children[i]
                    if(child.dataset.productid != el_id){
                      /* delete the item from the look/db and remove DOM from ui */
                      $.ajax({
                        success:function(response){
                          list.removeChild(child);
                        },
                        type: 'DELETE',
                        url: '/shopping_tool_api/look_item/' + child.dataset.lookitemid + '/'
                      });
                    }else if(child.dataset.productid == el_id){
                      match_count++;
                      if(match_count > 1){
                        /* delete the item from the look/db and remove DOM from ui */
                        $.ajax({
                          success:function(response){
                            list.removeChild(child);
                          },
                          type: 'DELETE',
                          url: '/shopping_tool_api/look_item/' + child.dataset.lookitemid + '/'
                        });                    
                      }
                    }
                  }
                }
              },
              type: 'PUT',
              url: '/shopping_tool_api/look_item/0/'
            });
          },
          onRemove: function(evt){
            var el = evt.item;
            /* delete the item from the look/db when removed from a drop box */
            $.ajax({
              success:function(response){},
              type: 'DELETE',
              url: '/shopping_tool_api/look_item/' + el.dataset.lookitemid + '/'
            });            
          }
        });        
      });
    });
    /* clone the contents of the rack for drag/drop */
    var rack_items = [];
    $.each($('#rack-list div.block'), function(idx){
      var block = $(this);
      var category = block.data('category');
      rack_items.push(
        '<a href="#" class="rack-section-toggle"><i class="fa fa-angle-down"></i>' + 
        category + '</a><div class="block" data-category="' + category + 
        '">'
      );
      $.each(block.find('div.item'), function(index){
        var item = $(this);
        rack_items.push(
          '<div class="item" data-productid="' + item.data('productid') + '">' +
          '<img class="handle" src="' + item.find('img').attr('src') + '"/></div>'
        );
      })
      rack_items.push('</div>');
    });
    /* add the clones and assign drag/drop functionality */
    var drag_rack = $('#rack-draggable');
    drag_rack.html(
      '<h2>' + $('#rack').find('h2').html() + 
      '</h2><div class="look-builder-rack">' + 
      rack_items.join('') + '</div>'
    );
    $.each(drag_rack.find('div.block'), function(idx){
      var box = $(this)[0];
      new Sortable(box, {
        handle: ".handle",
        group: { name: "look", pull: 'clone', put: false },
        sort: false,
        draggable: ".item"
      });
    });
    /* get look list to create compare */
    $.ajax({
      contentType : 'application/json',
      data: JSON.stringify({
        "client": parseInt($('#user-clip').data('userid')),
        "allume_styling_session": search_page.session_id,
        "stylist": parseInt($('#stylist').data('stylistid'))
      }),
      success:function(response){
        var markup = [];
        var comp_looks = $('#compare-looks');
        for(var i = 0, l = response.length; i<l; i++){
          var comp = response[i];
          if(comp.id != id){
            var look_products_markup = [];
            comp.look_products.sort(function(a,b){
              if(a.layout_position > b.layout_position){ return 1}
              if(a.layout_position < b.layout_position){ return -1}
              return 0;
            });
            for(var j = 0, prods = comp.look_products.length; j<prods; j++){
              var prod = comp.look_products[j];
              look_products_markup.push(
                '<div class="item" data-productid="' + prod.product.id + '">' +
                '<img class="handle" src="' + prod.product.product_image_url + '"/></div>'
              );
            }
            markup.push(
              '<div class="comp-look"><h3>' + comp.name + '</h3>' +
              '<span class="layout"><em>layout: </em>' + comp.look_layout.display_name + '</span>' +
              look_products_markup.join('') + '</div>'
            );
          }
        }
        /* display no looks message or add looks and drag/drop functionality */
        if(markup.length == 0){ 
          comp_looks.html('<span class="no-looks">no looks ready to compare</span>'); 
        }else if(markup.length > 0){
          comp_looks.html('<h2>Compare other looks</h2><div class="other-looks">' + markup.join('') + '</div>');
          $.each(comp_looks.find('div.comp-look'), function(idx){
            var box = $(this)[0];
            new Sortable(box, {
              handle: ".handle",
              group: { name: "look", pull: 'clone', put: false },
              sort: false,
              draggable: ".item"
            });
          });
        }
      },
      type: 'POST',
      url: '/shopping_tool_api/look_list/'
    });
  }
}