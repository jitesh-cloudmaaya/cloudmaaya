var look_builder = {
  newLookLink: function(data){
    var layout_name = ''
    for(var i = 0, l = look_layouts.length; i<l; i++){
      var layout = look_layouts[i];
      if(layout.id == data.look_layout){
        layout_name = layout.display_name;
        break;
      }
    }
    $('#look-links').append(
      '<a href="#" class="look-link" data-lookid="' + data.id + '">' +
      '<table><tr><td></td><td><span>' + data.name + '</span>' +
      '<span>layout: ' + layout_name + '</span></td></tr></table></a>' 
    );
  }
}