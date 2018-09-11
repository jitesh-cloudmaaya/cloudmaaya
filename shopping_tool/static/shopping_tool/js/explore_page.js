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
  * @description cache of getLooks xhr object
  */
  fetch: '',  
  /**
  * @description cache of masonry object for explore layout
  */
  masonry : '',
  /** 
  * @description cache of styling session
  */
  session_id: '',
  /**
  * @description init function applying the functionality to the page elements
  */
  init: function(){
    rack_builder.init();
    /* cache the session id */
    explore_page.session_id = $('body').data('stylesession');
    /* explore page functionality */
    var looks_header = $('#looks-header');
    var explore_form = $('#explore-form');
    $('#all-looks-list').on('click','a.item-detail',function(e){
      e.preventDefault();
      var link = $(this);
      rack_builder.inspectItem(link, 'rack');
    }).on('click','a.view-look-details', function(e){
      e.preventDefault();
      var link = $(this);
      look_builder.lookDetails(link);
    }).on('click','a.favorite-look', function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('favorited')){
        var fave = link.data('faveid');
        var look_id = link.data('lookid');
        var index = explore_page.favorite_look_ids.indexOf(look_id);
        explore_page.favorite_look_ids.splice(index, 1);
        explore_page.favorite_looks.splice(index, 1);
        link.data('faveid','').removeClass('favorited').find('i').removeClass('fa-heart').addClass('fa-heart-o');
        $.ajax({
          contentType : 'application/json',
          error: function(response){
            console.log(response);
          },
          success:function(response){
            //console.log(response);
            rack_builder.getRackLooks('favorites', '#fave-looks');
          },
          type: 'DELETE',
          url: '/shopping_tool_api/user_look_favorite/' + fave + '/'
        }); 
      }else{
        var fave = {
          "stylist": parseInt($('#stylist').data('stylistid')) ,
          "look": parseInt(link.data('lookid'))     
        }
        link.addClass('favorited').find('i').removeClass('fa-heart-o').addClass('fa-heart');
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
            link.data('faveid', response.id)
            rack_builder.getRackLooks('favorites', '#fave-looks');
          },
          type: 'PUT',
          url: '/shopping_tool_api/user_look_favorite/0/'
        }); 
      }
    }).on('click','a.clone-look',function(e){
      e.preventDefault();
      var link = $(this);
      $('#cloning-look').fadeIn();
      $.ajax({
        error: function(response){
          console.log(response);
          $('#cloning-look').hide();
          alert('There was a problem copying the look...');
        },
        success: function(response){
          if(response != undefined && response.new_look_id != undefined){
            if (response.turnoff_store_flag){
              $('#cloning-look div.stage').html('<span class="cloned redirect_message">Removing products from turned off merchants...</span>')
              window.setTimeout(function(){
                window.location = '/look_builder/' + explore_page.session_id + '/?look=' + response.new_look_id
              },
              2000);
            }
            else{
              $('#cloning-look div.stage').html('<span class="cloned">Redirecting to your new look...</span>')
              window.setTimeout(function(){
                window.location = '/look_builder/' + explore_page.session_id + '/?look=' + response.new_look_id
              },
              500);
            }
          }else{
            $('#cloning-look').hide();
            alert('There was a problem copying the look...');
          }
        },
        type: 'PUT',
        url: '/shopping_tool_api/add_look_to_session/' + link.data('lookid') + '/' + explore_page.session_id + '/'
      });
    });
    /* infinte scroll/paging listen for when user scrolls within 100 px of bnottom of page */
    document.addEventListener('scroll', function(evt){
      var st = $(window).scrollTop();
      var dh = $(document).height();
      var wh = $(window).height(); 
      var tot = st + wh;
      /* sticky header checks */
      if(looks_header.hasClass('sticky') == false){
        if(st > 80){
          looks_header.addClass('sticky')
          explore_form.addClass('sticky')
        }
      }else{
        if(st < 80){
          looks_header.removeClass('sticky')
          explore_form.removeClass('sticky')
        }
      }
      /* load more looks check */
      if( (dh - 80) < tot ){
        var loader = $('#loader');
        if(loader.hasClass('active') == false){
          loader.addClass('active');
          var fields = loader.data();
          var lookup = fields.filter;
          lookup.page = fields.page;
          lookup.per_page = 12
          explore_page.getLooks(lookup);
        }
      }
    }, {
      capture: true,
      passive: true
    });
  },
  /**
  * @description process search form into json for API and submit
  */
  generateSearch: function(){
    var lookup = {};
    var stylist = $('#stylist-select').val();
    var name = $('#search-terms').val();
    var faves = $('#explore-only-faves').prop('checked');
    var totals = $('#total-price-range')[0].noUiSlider.get();
    var avgs = $('#avg-price-range')[0].noUiSlider.get();
    var total_minimum = parseFloat(totals[0]);
    var total_maximum = parseFloat(totals[1]);
    var avg_minimum = parseFloat(avgs[0]);
    var avg_maximum = parseFloat(avgs[1]);
    lookup.page = 1;
    lookup.per_page = 12;
    lookup.style_type = $('#explore-style').val().map(function(val, i){ return parseInt(val)});
    lookup.style_occasion = $('#explore-occasion').val().map(function(val, i){ return parseInt(val)}); 
    if(lookup.style_type.length == 0){ delete lookup.style_type; }  
    if(lookup.style_occasion.length == 0){ delete lookup.style_occasion; } 
    if((stylist != '')&&(stylist != ' ')){ lookup.stylist = stylist; }
    if(name != ''){ lookup.name = name; }
    if(faves == true){ lookup.favorites_only = "True"};
    if((total_minimum != 0)||(total_maximum != 10000)){
      lookup.total_look_price_minimum = total_minimum;
      lookup.total_look_price_maximum = total_maximum;
    }
    if((avg_minimum != 0)||(avg_maximum != 2000)){
      lookup.average_item_price_minimum = avg_minimum;
      lookup.average_item_price_maximum = avg_maximum; 
    }
    console.log(lookup);
    $('#loader').data('filter',lookup);
    $('#all-looks-list').html('');
    explore_page.getLooks(lookup);
  },
  /**
  * @description function to fetch looks for the explore list
  * @param {object} lookup - json representation of fields to pass to API
  */  
  getLooks: function(lookup){
    /**
    * @description logic to make sure only one looks_list call happends at a time
    */
    if((typeof explore_page.fetch == 'object')&&(explore_page.fetch.readyState != 4)){
      explore_page.fetch.abort();
    }
    /* add is_published and with_products flags */
    lookup.is_published = 'True';
    lookup.with_products = 'False';
    $('#looks-header h2').html('loading looks...');
    explore_page.fetch = $.ajax({
      contentType : 'application/json',
      data: JSON.stringify(lookup),
      success:function(response){
        //console.log(response)
        explore_page.looksDisplay(response);
      },
      type: 'POST',
      url: '/shopping_tool_api/look_list/'
    });    
  },
  /**
  * @description add looks to the DOM/UI
  * @param {object} list_object look_list object
  */
  looksDisplay: function(list_object){
    var div = $('#all-looks-list');
    console.log(list_object.looks)
    for(var i = 0, l = list_object.looks.length; i<l; i++){
      var look = list_object.looks[i];
      var markup = [];
      var merchants = [];
      var prices = [];
      var look_fave_link = '<a href="#" title="Favorite look" class="favorite-look" data-lookid="' + 
        look.id + '"><i class="fa fa-heart-o"></i></a>';
      var look_fave_idx = explore_page.favorite_look_ids.indexOf(look.id);
      if(look_fave_idx > -1){
        var look_favorite_object = explore_page.favorite_looks[look_fave_idx];
        look_fave_link = '<a href="#" class="favorite-look favorited" data-lookid="' + 
        look.id + '" data-faveid="' + look_favorite_object.id + 
        '" title="Unfavorite look"><i class="fa fa-heart"></i></a>';
      }
      var collage_img = '<div class="collage-placeholder">collage not yet created</div>';
      if(look.collage != null){
        collage_img = '<a href="#" class="view-look-details" data-look="' + look.id + 
            '"><img class="collage" src="' + look.collage + '"/></a>';
      }
      markup.push(
        '<div class="look"><div class="display">' + look_fave_link  +
        '<a href="#" class="clone-look" title="Copy look, products from turned-off merchants will NOT be copied" data-lookid="' + look.id + 
        '"><i class="fa fa-clone"></i></a><h3><em data-lookid="' + 
        look.id + '">' + look.name + '</em><span>by ' + look.stylist.first_name + 
        ' ' + look.stylist.last_name + '</span></h3>' + collage_img
      );

      var avg_price = '';
      var occasions = '';
      var stores = '';
      var styles = '';
      var total_price = '';    
      var desc = look.description != '' ? '<p class="desc" title="' + look.description + '"><em>Description:</em><span>' + look.description + '</span></p>' : '';
      if(merchants.length > 0){
        merchants = [...new Set(merchants)];
        var last_class = prices.length == 0 ? 'last' : '' ;
        stores = '<p class="extras ' + last_class + '"><em>Stores:</em> ' + merchants.join(', ') + '</p>';
      }
      if(look.look_style_types != undefined && look.look_style_types.length > 0){
        styles = '<p class="extras"><em>Style:</em>' + 
        look.look_style_types.map(function(x, i){ return x.name}).join(', ') + '</p>';
      }
      if(look.look_style_occasions != undefined && look.look_style_occasions.length > 0){
        occasions = '<p class="extras"><em>Occasions:</em>' + 
        look.look_style_occasions.map(function(x, i){ return x.name}).join(', ') + '</p>';
      }      
      if(look.look_metrics[0] != undefined){
        total_price = numeral(parseFloat(look.look_metrics[0].total_look_price)).format('$0,0.00');
        avg_price = numeral(parseFloat(look.look_metrics[0].average_item_price)).format('$0,0.00');
      }
      div.append(
        markup.join('') + '' + stores +
        '<p class="extras"><em>Total price:</em> ' + total_price + 
        '</p><p class="extras"><em>Average item price:</em> ' + avg_price +
        '</p>' + styles + '' + occasions + '' + desc + '</div></div>'
      );
    }
    if(list_object.page == 1){
      if(typeof explore_page.masonry == 'object'){
        explore_page.masonry.remove();
      }
      explore_page.masonry = Macy({
          container: '#all-looks-list',
          trueOrder: true,
          waitForImages: false,
          margin: 8,
          columns: 3
      });
    }else{
      explore_page.masonry.recalculate();
    }
    var num = div.find('div.look').length
    var plural = num == 1 ? '' : 's';
    var now_showing_text = 'Showing 1 - ' + numeral(num).format('0,0') + ' of ' + 
      numeral(list_object.total_looks).format('0,0') + ' Look' + plural + ''
    if(num == 0){
      now_showing_text = 'No looks to display'
    }else if(num == 1){
      now_showing_text = 'Showing 1 Look'
    }
    $('#looks-header').addClass('ready');
    $('#looks-header h2').html(now_showing_text);
    if((list_object.page + 1) <= list_object.num_pages){
      $('#loader').removeClass('active').data('page', list_object.page + 1);
    }
  },
  /**
  * @description search widget functionality
  */
  searchSetUp: function(){  
    var at_load_stylist = utils.readURLParams('set_stylist');  
    $('#stylist-select').val(' ').selectize({ create: false, score: function(){
        return function() {
            return 1;
        };
    }}).change(function(e){
      var dd = $(this);
      if(dd.val() != ''){
        explore_page.generateSearch();
      }
    });
    $('#explore-style').val('').selectize({ create: false, sortField: 'text'}).change(function(e){
      explore_page.generateSearch();
    });
    $('#explore-occasion').val('').selectize({ create: false, sortField: 'text'}).change(function(e){
      explore_page.generateSearch();
    });        
    if(at_load_stylist == null){
      /* get the initial page of looks */
      $('#loader').data('filter', {});
      explore_page.getLooks({per_page: 12});
    }else{
      $('#stylist-select')[0].selectize.setValue(at_load_stylist, true);
      /* get the initial page of looks for specified stylist */
      $('#loader').data('filter', {stylist: at_load_stylist});
      explore_page.getLooks({stylist: at_load_stylist, per_page: 12});      
    }
    $('#search-terms').val('').blur(function(){
      explore_page.generateSearch();
    }).keyup(function(event) {
      if (event.keyCode === 13) {
        explore_page.generateSearch();
      }
    });
    $('#explore-only-faves').prop('checked', false).click(function(){
      explore_page.generateSearch();
    });
    explore_page.searchSliders();
    $("#explore-form input.ranger").keydown(function(event) {
      // Allowing backspace, delete, enter
      if ( event.keyCode == 46 || event.keyCode == 8 || event.keyCode == 13 ) {
        
      }else {
        // Ensure that it is a number and stop the keypress
        if (event.keyCode < 48 || event.keyCode > 57 ) {
          event.preventDefault(); 
        } 
      }
    });    
    $('#clear-filters').click(function(e){
      e.preventDefault()
      var link = $(this);
      /* reset the stylist to all, search term, style, and occasions to blank */
      $('#stylist-select')[0].selectize.setValue(' ', true);
      $('#explore-style')[0].selectize.setValue('', true);
      $('#explore-occasion')[0].selectize.setValue('', true);
      $('#search-terms').val('');
      /* turn off favorites */
      $('#explore-only-faves').prop('checked', false);
      /* destroy sliders */
      $('#avg-price-range')[0].noUiSlider.destroy();
      $('#total-price-range')[0].noUiSlider.destroy();
      /* re-set up sliders with beginning values */
      explore_page.searchSliders();
      /* generate new search */
      explore_page.generateSearch();
    });
  },
  /*
  * @description independent function to set up sliders allowing for destruction on clear filter press
  */
  searchSliders: function(){
    var total_slider = $('#total-price-range')[0];
    var total_slider_min = $('#total-price-min')[0];
    var total_slider_max = $('#total-price-max')[0];
    var total_slider_inputs = [total_slider_min, total_slider_max];
    noUiSlider.create(total_slider, {
      start: [0, 10000],
      behaviour: 'drag',
      connect: true,
      range: {
        'min': [0],
        'max': [10000]
      }
    });
    var avg_slider = $('#avg-price-range')[0];
    var avg_slider_min = $('#avg-price-min')[0];
    var avg_slider_max = $('#avg-price-max')[0];
    var avg_slider_inputs = [avg_slider_min, avg_slider_max];
    noUiSlider.create(avg_slider, {
      start: [0, 2000],
      behaviour: 'drag',
      connect: true,
      range: {
        'min': [0],
        'max': [2000]
      }
    });
    total_slider.noUiSlider.on('update', function( values, handle ) {
      total_slider_inputs[handle].value = values[handle];
    });
    total_slider.noUiSlider.on('set', function() {
      explore_page.generateSearch();
    });    
    total_slider_inputs.forEach(function(input, handle) {
      input.addEventListener('change', function(){
        var r = [null,null];
        r[handle] = this.value;
        total_slider.noUiSlider.set(r);
      });
    });
    avg_slider.noUiSlider.on('update', function( values, handle ) {
      avg_slider_inputs[handle].value = values[handle];
    });
    avg_slider.noUiSlider.on('set', function() {
      explore_page.generateSearch();
    });    
    avg_slider_inputs.forEach(function(input, handle) {
      input.addEventListener('change', function(){
        var r = [null,null];
        r[handle] = this.value;
        avg_slider.noUiSlider.set(r);
      });
    });
  }
}