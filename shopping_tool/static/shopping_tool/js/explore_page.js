/**
* @description explore_page namespace object, conatining the functionality and templates for the explore page
*/
var explore_page = {
  /**
  * @description cache of all looks for in page filtering
  */
  all_looks: [],
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
    explore_page.session_id = $('body').data('stylesession');
    $('#loader').data('filter', {});
    /* get the initial page of looks */
    getLooks({});
    $('#stylist-select').val(' ').selectize({ create: false, sortField: 'text'});
    $('#look-name').val('');
    $('#all-looks-list').on('click','a.item-detail',function(e){
      e.preventDefault();
      var link = $(this);
      rack_builder.inspectItem(link);
    });
    /* get new filtered list of looks */
    $('#looks-filter').click(function(e){
      e.preventDefault();
      var lookup = {};
      var stylist = $('#stylist-select').val();
      var name = $('#look-name').val();
      lookup.page = 1
      console.log(stylist)
      if((stylist != '')&&(stylist != ' ')){ lookup.stylist = stylist; }
      if(name != ''){ lookup.name = name; }
      console.log(lookup)
      $('#loader').data('filter',lookup);
      $('#all-looks-list').html('');
      getLooks(lookup);
    });
    /* infinte scroll/paging listen for when user scrolls within 100 px of bnottom of page */
    $(window).scroll(function(){
      var st = $(window).scrollTop();
      var dh = $(document).height();
      var wh = $(window).height(); 
      var tot = st + wh;
      if( (dh - 100) < tot ){
        var loader = $('#loader');
        if(loader.hasClass('active') == false){
          loader.addClass('active');
          var fields = loader.data();
          var lookup = fields.filter;
          lookup.page = fields.page;
          getLooks(lookup);
        }
      }
    });
    /**
    * @description private function to fetch additional looks for the explore list
    * @param {object} lookup - json representation of fields to pass to API
    */
    function getLooks(lookup){
      $('#looks-header').html('');
      $.ajax({
        contentType : 'application/json',
        data: JSON.stringify(lookup),
        success:function(response){
          console.log(response)
          explore_page.looksDisplay(response);
        },
        type: 'POST',
        url: '/shopping_tool_api/look_list/'
      });
    }
  },
  /**
  * @description add looks to the DOM/UI
  * @param {object} list_object look_list object
  */
  looksDisplay: function(list_object){
    var div = $('#all-looks-list');
    for(var i = 0, l = list_object.looks.length; i<l; i++){
      var look = list_object.looks[i];
      var markup = [];
      markup.push(
        '<div class="look"><div class="display">' +
        '<a href="#" data-lookid="' + look.id + '" class="favorite-look"><i class="fa fa-heart-o"></i></a>' +
        '<h3>' + look.name + '<span>by ' + 
        stylist_names[look.stylist] + '</span></h3><div class="items">' 
      );
      look.look_products.sort(function(a,b){
        if(a.layout_position > b.layout_position){ return 1}
        if(a.layout_position < b.layout_position){ return -1}
        return 0;
      });
      for(var j = 0, prods = look.look_products.length; j<prods; j++){
        var prod = look.look_products[j];
        var fave_link = '<a href="#" class="favorite" data-productid="' + 
          prod.product.id + '"><i class="fa fa-heart-o"></i></a>';
        var fave_idx = rack_builder.favorites_product_ids.indexOf(prod.product.id );
        if(fave_idx > -1){
          var favorite_object = rack_builder.favorites[fave_idx];
          fave_link = '<a href="#" class="favorite favorited" data-productid="' + 
          prod.product.id + '" data-faveid="' + favorite_object.id + '"><i class="fa fa-heart"></i></a>';
        }
        markup.push(
          '<div class="item" data-productid="' + prod.product.id + '"><a href="#" class="item-detail" ' + 
          'data-name="' + prod.product.product_name + '" data-brand="' + prod.product.manufacturer_name + 
          '" data-productid="' + prod.product.id + '"><img src="' + prod.product.product_image_url + 
          '"/></a></div>'
        );
      }
      markup.push('</div></div></div>');
      div.append(markup.join(''))
    }
    var num = div.find('div.look').length
    var plural = num == 1 ? '' : 's';
    $('#looks-header').html('<h2><em>' + num + '</em> Look' + plural + '</h2>');
    if((list_object.page + 1) <= list_object.num_pages){
      $('#loader').removeClass('active').data('page', list_object.page + 1);
    }
  }
}