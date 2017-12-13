/**
* @description explore_page namespace object, conatining the functionality and templates for the explore page
*/
var explore_page = {
  /**
  * @description cache of all looks for in page filtering
  */
  all_looks: [],
  /**
  * @description cache array of stylist's favorite looks, updated at load
  */
  favorite_looks: [],
  /**
  * @description cache array of favorited look ids, used to set correct favorite link 
  */
  favorite_look_ids: [],  
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
    }).on('click','a.favorite-look', function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('favorited')){
        var fave = link.data('faveid');
        var look_id = link.data('lookid');
        var index = explore_page.favorite_look_ids.indexOf(look_id);
        explore_page.favorite_look_ids.splice(index, 1);
        explore_page.favorite_looks.splice(index, 1);
        $.ajax({
          contentType : 'application/json',
          error: function(response){
            console.log(response);
          },
          success:function(response){
            //console.log(response);
            link.data('faveid','').removeClass('favorited').find('i').removeClass('fa-heart').addClass('fa-heart-o');
          },
          type: 'DELETE',
          url: '/shopping_tool_api/user_look_favorite/' + fave + '/'
        }); 
      }else{
        var fave = {
          "stylist": parseInt($('#stylist').data('stylistid')) ,
          "look": parseInt(link.data('lookid'))     
        }
        $.ajax({
          contentType : 'application/json',
          data: JSON.stringify(fave),
          error: function(response){
            console.log(response);
          },
          success:function(response){
            //console.log(response);
            explore_page.favorite_looks.push(response);
            explore_page.favorite_look_ids.push(response.look);
            link.data('faveid', response.id).addClass('favorited').find('i').removeClass('fa-heart-o').addClass('fa-heart');
          },
          type: 'PUT',
          url: '/shopping_tool_api/user_look_favorite/0/'
        }); 
      }
    });
    /* get new filtered list of looks */
    $('#looks-filter').click(function(e){
      e.preventDefault();
      var lookup = {};
      var stylist = $('#stylist-select').val();
      var name = $('#look-name').val();
      lookup.page = 1
      //console.log(stylist)
      if((stylist != '')&&(stylist != ' ')){ lookup.stylist = stylist; }
      if(name != ''){ lookup.name = name; }
      //console.log(lookup)
      $('#loader').data('filter',lookup);
      $('#all-looks-list').html('');
      getLooks(lookup);
    });
    var looks_header = $('#looks-header');
    /* infinte scroll/paging listen for when user scrolls within 100 px of bnottom of page */
    $(window).scroll(function(){
      var st = $(window).scrollTop();
      var dh = $(document).height();
      var wh = $(window).height(); 
      var tot = st + wh;
      if(looks_header.hasClass('sticky') == false){
        if(st > 148){
          looks_header.addClass('sticky')
        }
      }else{
        if(st < 148){
          looks_header.removeClass('sticky')
        }
      }
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
          //console.log(response)
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
    var cropped_images = [];
    for(var i = 0, l = list_object.looks.length; i<l; i++){
      var look = list_object.looks[i];
      var markup = [];
      var look_fave_link = '<a href="#" class="favorite-look" data-lookid="' + 
        look.id + '"><i class="fa fa-heart-o"></i></a>';
      var look_fave_idx = explore_page.favorite_look_ids.indexOf(look.id);
      if(look_fave_idx > -1){
        var look_favorite_object = explore_page.favorite_looks[look_fave_idx];
        look_fave_link = '<a href="#" class="favorite-look favorited" data-lookid="' + 
        look.id + '" data-faveid="' + look_favorite_object.id + '"><i class="fa fa-heart"></i></a>';
      }
      markup.push(
        '<div class="look"><div class="display">' + look_fave_link  +
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
        var src = prod.product.product_image_url;
        if(prod.cropped_dimensions != null){
          var crop = {
            id: 'look-' + look.id + '-item-' + prod.id,
            src: look_proxy + '' + src,
            dims: prod.cropped_dimensions
          }
          cropped_images.push(crop);
        }
        markup.push(
          '<div class="item" data-productid="' + prod.product.id + '"><a href="#" class="item-detail" ' + 
          'data-name="' + prod.product.product_name + '" data-brand="' + prod.product.manufacturer_name + 
          '" data-productid="' + prod.product.id + '"><span id="look-' + look.id + '-item-' + prod.id + 
          '"><img src="' + src + '"/></a></div>'
        );
      }
      markup.push('</div></div></div>');
      div.append(markup.join(''))
    }
    if(cropped_images.length > 0){
      for(var i = 0, l = cropped_images.length; i<l; i++){
        look_builder.getCroppedImage(cropped_images[i], '#all-looks-list');
      }
    }
    var num = div.find('div.look').length
    var plural = num == 1 ? '' : 's';
    $('#looks-header').html('<h2>Showing 1 - ' + num + ' of ' + list_object.total_looks + ' Look' + plural + '</h2>');
    if((list_object.page + 1) <= list_object.num_pages){
      $('#loader').removeClass('active').data('page', list_object.page + 1);
    }
  }
}