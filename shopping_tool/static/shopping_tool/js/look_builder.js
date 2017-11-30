/**
* @description look builder name space containing functionality for building looks
*/
var look_builder = {
  /**
  * @description look builder ui/ux functionality
  */
  functionality: function(){
    $('#close-design-look').click(function(e){
      e.preventDefault();
      $('#design-look').addClass('hide')
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
      console.log(result)
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
      look_drop.html(
        '<div class="instructions"><div id="look-trash"></div>' +
        'Drag rack items from the left into open spots within the look layout.' +
        '<br/><br/>Dragging an item into an occupied spot will remove the old item ' +
        'from that position.<br/><br/>Drag items to trash to remove from the look.<br/><br/>' + 
        'Compare to other looks for the client to the right.' +
        '</div><div class="drop-zone">' + markup.join('') + '</div>'
      );
      var col_widths = 0;
      $.each(look_drop.find('div.column'), function(idx){
        col_widths += $(this).outerWidth();
      });

      look_drop.find('div.column:first-child').css('marginLeft', ((look_drop.width() * 0.75) - col_widths)/2);
      /* add the trash functionality */
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
                el.setAttribute('data-lookitemid', response.id)
              },
              type: 'PUT',
              url: '/shopping_tool_api/look_item/0/'
            });
            if(list.children.length > 1){
              for(var i = 0, l = list.children.length; i<l; i++){
                var child = list.children[i]
                if(child.dataset.productid != el_id){
                  /* delete the item from the look and remove it from ui */
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
          },
          onRemove: function(evt){
            var el = evt.item;
            /* delete the item from the look when removed from a drop box */
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
    $.each($('#rack-list div.item'), function(idx){
      var item = $(this);
      rack_items.push(
        '<div class="item" data-productid="' + item.data('productid') + '">' +
        '<img class="handle" src="' + item.find('img').attr('src') + '"/></div>'
      )
    });
    /* add the clones and assign drag/drop functionality */
    var drag_rack = $('#rack-draggable');
    drag_rack.html(rack_items.join(''));
    new Sortable(drag_rack[0], {
      handle: ".handle",
      group: { name: "look", pull: 'clone', put: false },
      sort: false,
      draggable: ".item"
    });
    /* create other looks ui */
  }
}