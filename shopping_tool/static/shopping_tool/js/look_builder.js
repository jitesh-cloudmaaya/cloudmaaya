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
      var markup = [];
      for(var i = 0; i<result.look_layout.columns; i++){
        var col = ['<div class="column" id="lookdropcol' + i + '">'];
        var heights = result.look_layout.row_heights.split(',');
        for(var j = 0; j<result.look_layout.rows; j++){
          var h = heights[j];
          col.push('<div class="row" style="height:calc(' + h + '% - 6px)"></div>');
        }
        col.push('</div>');
        markup.push(col.join(''));
      }
      $('#look-drop').html(
        '<div class="instructions left">Drag rack items from the left into open spots ' +
        'within the look layout.<br/><br/>Compare to other looks for the client to the right.' +
        '</div><div class="drop-zone">' + markup.join('') + '</div>'
      );
      $.each($('#look-drop div.column div.row'), function(idx){
        var box = $(this)[0];
        new Sortable(box, {
          handle: ".handle",
          group: { name: "look", pull: true, put: true },
          sort: true,
          draggable: ".item"})        
      })


    })

    /* clone the contents of the rack for drag/drop */
    var rack_items = [];
    $.each($('#rack-list div.item'), function(idx){
      var item = $(this);
      rack_items.push(
        '<div class="item" data-productid="' + item.data('productid') + '">' +
        '<img class="handle" src="' + item.find('img').attr('src') + '"/></div>'
      )
    });
    var drag_rack = $('#rack-draggable');
    drag_rack.html(rack_items.join(''));
    var sortable = new Sortable(drag_rack[0], {
        handle: ".handle",
        group: { name: "look", pull: 'clone', put: false },
        sort: true,
        draggable: ".item"})


    
  }
}