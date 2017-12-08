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
    $('#all-looks-list').on('click','a.favorite-look', function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('favorited')){
        link.removeClass('favorited').find('i').removeClass('fa-heart').addClass('fa-heart-o');
      }else{
        link.addClass('favorited').find('i').removeClass('fa-heart-o').addClass('fa-heart');
      }
    }).on('click','a.favorite',function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('favorited')){
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
            link.data('faveid','').removeClass('favorited').find('i').removeClass('fa-heart').addClass('fa-heart-o');
          },
          type: 'DELETE',
          url: '/shopping_tool_api/user_product_favorite/' + fave + '/'
        }); 
      }else{
        var fave = {
          "stylist": parseInt($('#stylist').data('stylistid')) ,
          "product": parseInt(link.data('productid'))     
        }
        $.ajax({
          contentType : 'application/json',
          data: JSON.stringify(fave),
          error: function(response){
            console.log(response);
          },
          success:function(response){
            console.log(response);
            rack_builder.favorites.push(response);
            rack_builder.favorites_product_ids.push(response.product);
            link.data('faveid', response.id).addClass('favorited').find('i').removeClass('fa-heart-o').addClass('fa-heart');
          },
          type: 'PUT',
          url: '/shopping_tool_api/user_product_favorite/0/'
        }); 
      }
    }).on('click','a.add-to-rack',function(e){
      e.preventDefault();
      var link = $(this);
      rack_builder.addToRack(link, 'explore');
    }).on('click','a.details',function(e){
      e.preventDefault();
      var link = $(this);
      var product = link.data('details');
      var retail = product.retail_price;
      var sale = product.sale_price;
      var price_display = '';
      var merch = '<span class="merch">' + product.merchant_name + '</span>';
      var manu = '<span class="manu">by ' + product.manufacturer_name + '</span>';    
      if((sale >= retail)||(sale == 0)){
        price_display = '<span class="price"><em class="label">price:</em>' + 
          numeral(retail).format('$0,0.00') + '</span>';
      }else{
        price_display = '<span class="price"><em class="label">price:</em><em class="sale">(' + 
          numeral(retail).format('$0,0.00') + ')</em>' + numeral(sale).format('$0,0.00') + '</span>';
      }   
      $('#inspect-item').html(
        '<div class="stage"><a href="#" class="close-inspect"><i class="fa fa-times"></i></a>' +
        '<h2>' + product.product_name + '</h2><table>' +
        '<tr><td class="img"><img src="' + product.product_image_url + '"/></td>' +
        '<td class="details"><a href="' + product.product_url + '" target="_blank" class="name">' + 
        product.product_name + '</a>' +  merch + '' + manu + '<p class="item-desc"> '+ 
        product.short_product_description + '</p>' + price_display +
        '<span class="general"><em>size:</em>' + product.size + '</span>' +
        '<span class="general"><em>category:</em>' + product.primary_category + 
        '</span></td></tr></table></div>'
      ).fadeIn();
    });
    $('#inspect-item').on('click', 'a.close-inspect', function(e){
      e.preventDefault();
      $('#inspect-item').fadeOut();
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
          '<div class="item" data-productid="' + prod.product.id + '">' + 
          '<img src="' + prod.product.product_image_url + '"/>' +
          '<div class="link-bar"><a href="#" class="details"><i class="fa fa-search"></i></a>' + 
          fave_link + '<a href="#" class="add-to-rack"><i class="icon-hanger"></i></a></div></div>'
        );
      }
      markup.push('</div></div></div>');
      div.append(markup.join(''))
      $.each(div.find('.look:last-child div.item'), function(idx){
        var itm = $(this);
        itm.find('a.details').data('details', look.look_products[idx].product);
        itm.find('a.add-to-rack').data('details', look.look_products[idx].product);
      });
    }
    var num = div.find('div.look').length
    var plural = num == 1 ? '' : 's';
    $('#looks-header').html('<h2><em>' + num + '</em> Look' + plural + '</h2>');
    if((list_object.page + 1) <= list_object.num_pages){
      $('#loader').removeClass('active').data('page', list_object.page + 1);
    }
  }
}