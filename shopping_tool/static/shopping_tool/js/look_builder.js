/**
* @description look builder name space containing functionality for create look UI/ux for building looks
*/
var look_builder = {
  /** 
  * @description cache of styling session
  */
  session_id: '',  
  /**
  * @description gather the compare looks objects and create markup for display
  * @param {object} lookup - json data for API call
  * @param {integer} loopk_id - id of currently being edited look
  */  
  compareLooksMarkup: function(lookup, look_id){
    var comp_looks = $('#compare-looks div.other-looks');
    $.ajax({
      contentType : 'application/json',
      data: JSON.stringify(lookup),
      success:function(response){
        console.log(response)
        var markup = [];
        for(var i = 0, l = response.looks.length; i<l; i++){
          var comp = response.looks[i];
          if(comp.id != look_id){
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
          comp_looks.html(markup.join(''));
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
  },
  /**
  * @description look builder ui/ux functionality
  */
  functionality: function(){
    /* cache the session id */
    look_builder.session_id = $('body').data('stylesession');    
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
       "allume_styling_session": look_builder.session_id,
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
    Mousetrap.bind('shift+q+w', function(e) {
      $('#new-look-error').html('');
      $('#new-look-name').val('');
      $('#new-look-layout')[0].selectize.setValue('',true);      
      $('#create-look').fadeToggle();
      return false;
    });       
    $('#close-design-look').click(function(e){
      e.preventDefault();
      $('#design-look').addClass('hide');
      $('#rack-draggable').html('');
      $('#look-drop').html('');
      $('#compare-looks').html('');
    });
    $('#rack-draggable').on('click','a.close-all-rack-sections', function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('open-all') == false){
        link.addClass('open-all').html('<i class="fa fa-caret-square-o-down"></i>expand all sections');
        $.each($('#rack-draggable').find('a.rack-section-toggle'),function(idx){
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
        $.each($('#rack-draggable').find('a.rack-section-toggle'),function(idx){
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
    $('#compare-looks').on('click','a.look-filter', function(e){
      e.preventDefault();
      var link = $(this);
      link.toggleClass('open')
      $('#look-filter-options').toggleClass('show');
    }).on('click','a.submit-filter-btn', function(e){
      var comp_looks = $('#compare-looks');
      e.preventDefault();
      var link = $(this);
      var look_id = link.data('look');
      var checked = [];
      $.each($('#look-filter-options input:checked'), function(idx){ checked.push($(this).attr('name')); })
      var link_text = '';
      var lookup = {};
      if((checked.indexOf('session') > -1)||(checked.length == 0)){
        link_text = 'session looks';
        lookup.allume_styling_session = look_builder.session_id
      }else{
        link_text = checked.join('/') + ' looks';
        if(checked.indexOf('stylist') > -1){
          lookup.stylist = parseInt($('#stylist').data('stylistid'));
        }
        if(checked.indexOf('client') > -1){
          lookup.client = parseInt($('#user-clip').data('userid'));         
        }
      }
      lookup.name = $('#look-filter-options input.filter').val();
      comp_looks.find('a.look-filter').html(link_text + ' <i class="fa fa-caret-down"></i>').removeClass('open');
      $('#look-filter-options').removeClass('show');
      look_builder.compareLooksMarkup(lookup, look_id);
    });
    $('#look-indepth').on('click', 'a.close-indepth', function(e){
      e.preventDefault();
      $('#look-indepth').fadeOut();
    });
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
    var links = $('#look-links');
    links.append(
      '<a href="#" class="look-link" data-lookid="' + data.id + '" data-lookname="' + data.name + '">' +
      '<table><tr><td class="icon"><i class="fa fa-shopping-bag"></i></td>' +
      '<td><span class="name">' + data.name + '</span>' +
      '<span class="layout"><em>layout:</em> ' + layout_name + 
      '</span></td></tr></table></a>' 
    );
    var look_count = links.find('a.look-link').length;
    var plural = look_count == 1 ? '' : 's';
    $('#look-list h2').html(look_count + ' Look' + plural);
  },
  /**
  * @description set up the builder ui/ux from clicked look link
  * @param {integer} id -  the look id 
  */
  setUpBuilder: function(id){
    /* get the look settings to build the drop zone */
    $.get('/shopping_tool_api/look/' + id + '/', function(result){
      console.log(result)
      var look_drop = $('#look-drop');
      /* dynamically generate the width of look columns */
      var available_space = (look_drop.width() * 0.75) - 20;
      var col_width_margins = result.look_layout.columns * 5;
      var col_width = (available_space - col_width_margins)/result.look_layout.columns;
      var markup = [];
      for(var i = 0; i<result.look_layout.columns; i++){
        var col = ['<div class="column" id="lookdropcol' + i + '" style="width:' + col_width + 'px">'];
        var heights = result.look_layout.row_heights.split(',');
        for(var j = 0; j<result.look_layout.rows; j++){
          var h = heights[j];
          var position = i > 0 ? ((j + 1) + (i * result.look_layout.rows)) : j + 1 ;
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
            var box = $(list);
            var col = box.closest('div.column')
            var col_idx = col.index();
            if(col_idx != 0){
              position += (col_idx * col.find('div.row').length);
            }
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
    var rack_cats = $('#rack-list div.block');
    if(rack_cats.length > 0){
      rack_items.push(
        '<a class="close-all-rack-sections" href="#">' +
        '<i class="fa fa-caret-square-o-up"></i>collapse all sections</a>'
      );
    }  
    $.each(rack_cats, function(idx){
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
    /* create compare looks scaffolding and get looks */
    $('#compare-looks').html(
      '<h2>Compare <a href="#" class="look-filter">session looks <i class="fa fa-caret-down"></i></a></h2>' +
      '<div id="look-filter-options"><label class="toggle">' +
      '<input name="session" type="checkbox" checked><span><small></small></span>' +
      '<em>session looks</em></label><label class="toggle">' +
      '<input name="stylist" type="checkbox"><span><small></small></span>' +
      '<em>stylist looks</em></label><label class="toggle">' +
      '<input name="client" type="checkbox"><span><small></small></span>' +
      '<em>client looks</em></label><input type="text" placeholder="' +
      'Enter filter keywords..." class="filter"/><div class="look-filter-submit">' +
      '<a href="#" class="submit-filter-btn" data-look="' + id + '">filter looks</a></div></div>' +
      '<div class="other-looks"></div>'
    );
    var lookup = {
      "client": parseInt($('#user-clip').data('userid')),
      "allume_styling_session": look_builder.session_id,
      "stylist": parseInt($('#stylist').data('stylistid'))
    }
    look_builder.compareLooksMarkup(lookup, id);
  }
}