/**
* @description look builder name space containing functionality for create look UI/ux for building looks
*/
var look_builder = {
  /** 
  * @description cache of styling session
  */
  session_id: '',
  /** 
  * @description cache of stylist id
  */
  stylist_id: '',    
  /**
  * @description gather the compare looks objects and create markup for display
  * @param {object} lookup - json data for API call
  * @param {integer} at_load - id of currently being edited look or null
  */  
  editableLooksMarkup: function(looks){
    console.log(looks)
    var at_load = utils.readURLParams('look');
    var comp_looks = $('#compare-looks div.other-looks');
    var markup = [];
    looks.sort(function(a,b){
      if(a.position > b.position){ return 1}
      if(a.position < b.position){ return -1}
      return 0;
    });
    for(var i = 0, l = looks.length; i<l; i++){
      markup.push(look_builder.lookMarkupGenerator(looks[i], 'comp', at_load));
    }
    /* display no looks message or add looks and drag/drop functionality */
    if(markup.length == 0){ 
      comp_looks.html('<span class="no-looks" id="no-look-display">add some looks...</span>'); 
    }else if(markup.length > 0){
      comp_looks.html(markup.join(''));
      if(at_load != null){
        $('#compare-looks div.comp-look:not(".editing")').addClass('off');
      }
      /* ordering of the looks */
      new Sortable(document.getElementById('look-builder-session-looks'), {
          handle: ".look-name-header",
          draggable: ".comp-look",
          onUpdate: function (evt){
            $.each($('#look-builder-session-looks div.comp-look'), function(idx){
              var look = $(this);
              var position_obj = {
                look_id: look.data('lookid'),
                position: look.index() + 1
              }
              $.ajax({
                contentType : 'application/json',
                data: JSON.stringify(position_obj),
                type: 'PUT',
                url: '/shopping_tool_api/update_look_position/' + look.data('lookid') + '/'
              });
            })
          }
        }
      );
    }
  },
  /**
  * @description look builder ui/ux functionality
  */
  functionality: function(){
    $('#add-new-look-to-lookbook').click(function(e){
      e.preventDefault();
      var link = $(this);
      var edit_status = $('#look-drop').find('div.start').length;
      if(edit_status != 1){
        $('#finish-editing-look').trigger('click');
      }
      $('#look-drop').html('<div class="start">building look editor...</div>');
      $.ajax({
        contentType : 'application/json',
        data: JSON.stringify({
         "name": '',
         "description": '',
         "allume_styling_session": look_builder.session_id,
         "stylist": look_builder.stylist_id,
         "collage": null     
        }),
        error: function(response){

        },
        success:function(response){
          link.removeClass('loading')
          look_builder.setUpBuilder(response.id);
          $('#no-look-display').remove();
          $.get('/shopping_tool_api/look/' + response.id + '/', function(result){
            $('#compare-looks div.other-looks').prepend(look_builder.lookMarkupGenerator(result, 'comp', null));
            var new_div = $('#compare-looks div.other-looks div.comp-look:nth-child(1)');
            new_div.addClass('editing').siblings('div.comp-look').removeClass('editing off').addClass('off')
          });
        },
        type: 'PUT',
        url: '/shopping_tool_api/look/0/'
      })
    });
    $('#look-layouts-container').on('click', 'label.layout-check', function(e){
      var box = $(this);
      if(box.hasClass('selected') == false){
        box.addClass('selected').siblings('label.layout-check').removeClass('selected');
      }
    });
    $('#compare-looks').on('click', 'a.edit-look-btn', function(e){
      e.preventDefault();
      var link = $(this);
      var look = link.data('lookid');
      var div = link.closest('div.comp-look');
      div.addClass('editing').siblings('div.comp-look').removeClass('editing').addClass('off');
      look_builder.setUpBuilder(look);
      $('#publish-lookbook').data('allowed', 'false');
    }).on('click', 'a.delete-look-btn', function(e){
      e.preventDefault();
      var link = $(this);
      var look = link.data('lookid');
      $('#delete-look-overlay').find('a.yes').data('lookid', look).end().fadeIn();
    }).on('click','a.view-look-details', function(e){
      e.preventDefault();
      var link = $(this);
      look_builder.lookDetails(link);
    })
    /* delete look confirm dialog */
    $('#delete-look-overlay').find('a.yes').click(function(e){
      e.preventDefault();
      var link = $(this);
      $('#client-look-id-' + link.data('lookid')).remove();
      $.ajax({
        success:function(r){
          //console.log(r)
        },
        type: 'DELETE',
        url: '/shopping_tool_api/look/' + link.data('lookid') + '/'
      });
      $('#delete-look-overlay').fadeOut();
      var remaining_looks = $('#compare-looks div.other-looks div.comp-look').length;
      if(remaining_looks == 0){
        $('#compare-looks div.other-looks').html('<span class="no-looks" id="no-look-display">add some looks...</span>');
      }
      $('#publish-lookbook').data('allowed', 'false');
    }).end().find('a.cancel').click(function(e){
      e.preventDefault();
      $('#delete-look-overlay').fadeOut();
    });
    $('#preview-lookbook').click(function(e){
      e.preventDefault();
      var edit_status = $('#look-drop').find('div.start').length;
      if(edit_status != 1){
        alert('You must finish editing your selected look before you can preview the lookbook.')
      }else{
        $('#previewIframe').attr('src', 'https://stage.allume.co/looks/' + $('body').data('sessiontoken') + '#preview');
        $('#preview-lookbook-overlay').fadeIn();
        $('#publish-lookbook').data('allowed', 'true');
      }
    });
    $('#publish-lookbook').click(function(e){
      e.preventDefault();
      var link = $(this);
      if(link.data('allowed') == 'true'){
        var lookup = {
          "client": parseInt($('#user-clip').data('userid')),
          "allume_styling_session": rack_builder.session_id,
          "page": 1
        }
        $.ajax({
          contentType : 'application/json',
          data: JSON.stringify(lookup),
          success:function(response){
            var markup = [];
            var cropped_images = [];
            var look_occasions = [];
            var look_styles = [];
            for(var i = 0, l = style_types.length; i<l; i++){
              var ls = style_types[i];
              look_styles.push(
                '<label class="toggle"><input value="' + ls.id + '" data-display="' + ls.name +
                '" class="style" type="checkbox"/><span><small></small></span><em>' +
                ls.name +'</em></label>'
              );
            }
            for(var i = 0, l = occasion_types.length; i<l; i++){
              var ls = occasion_types[i];
              look_occasions.push(
                '<label class="toggle"><input value="' + ls.id + '" data-display="' + ls.name +
                '" class="occ" type="checkbox"/><span><small></small></span><em>' +
                ls.name +'</em></label>'
              );
            }
            var half_styles = Math.ceil(look_styles.length / 2);
            var half_occs = Math.ceil(look_occasions.length / 2);
            var first_half_styles = look_styles.splice(0,half_styles);
            var first_half_occs = look_occasions.splice(0,half_occs);
            for(var i = 0, l = response.looks.length; i<l; i++){
              var look = response.looks[i];
              var collage_img = '<div class="collage-placeholder">no collage</div>';
              if(look.collage != null){
                collage_img = '<img class="collage" src="' + look.collage + '"/>';
              }
              markup.push(
                '<div class="pub-look" data-lookname="' + look.name + '" data-lookid="' + 
                look.id + '"><h5><span>' + look.name + '</span></h5>' +
                '<table class="categorize-look"><tr><td rowspan="2" class="collage">' +
                collage_img + '</td><td class="label">Style:</td>' +
                '<td class="label"></td><td class="label split">Occasion:</td>' +
                '<td class="label"></td></tr><tr>' +
                '<td>' + first_half_styles.join('') + '</td>' +
                '<td>' + look_styles.join('') + '</td>' +
                '<td class="split">' + first_half_occs.join('') + '</td>' +
                '<td>' + look_occasions.join('') + '</td></tr></table></div>'
              );
            }
            $('#pub-section1').html(
              '<div id="pub-section1-errors"></div>' + 
              '<a href="#" class="next-tab">next<i class="fa fa-chevron-right"></i></a>' +
              markup.join('')
            );
            /* settings the styles/occasions if they exist */
            for(var i = 0, l = response.looks.length; i<l; i++){
              var look = response.looks[i];
              var styles = look.look_style_types;
              var occasions = look.look_style_occasions;
              var div = $('#pub-section1 div.pub-look[data-lookid="' + look.id + '"]');
              for(var ix = 0, lx = styles.length; ix<lx; ix++){
                var style_type = styles[ix];
                div.find('input.style[value="' + style_type.id + '"]').prop('checked', true);
              }
              for(var ix = 0, lx = occasions.length; ix<lx; ix++){
                var style_occ = occasions[ix];
                div.find('input.occ[value="' + style_occ.id + '"]').prop('checked', true);                
              }              
            }
          },
          type: 'POST',
          url: '/shopping_tool_api/look_list/'
        });
        $('#pub-section1').html(
          '<div class="publish-loading">' +
          '<span class="pulse_loader"></span><span class="pulse_message">loading the looks for this lookbook...</span>' +
          '</div>'
        ).addClass('on').siblings('div').removeClass('on');
        $('#pub-wizard-step1').addClass('on').siblings('a').removeClass('on');
        $('#send-toggle').prop('checked', false);
        $('#send-later-wrapper').hide();
        var start_id = document.getElementById('send-later')
        rome(start_id, {
          initialValue:  moment().startOf('day').format('YYYY-MM-DD'),
          min: moment().startOf('day').format('YYYY-MM-DD'),
          time: true,
          timeFormat: 'h:mm a'
        });
        $('#publish-lookbook-overlay').fadeIn();
      }else{
        alert('You must preview the lookbook before you can publish.')
      }
    });
    $('#close-lb').click(function(e){
      e.preventDefault();
      $('#publish-lookbook-overlay').fadeOut();
    });
    $('#close-lb-pre').click(function(e){
      e.preventDefault();
      $('#preview-lookbook-overlay').fadeOut();
    }); 
    /* wizard tabs, their status checking and other functionality for publish lookbook */
    $('#pub-section1').on('click', 'a.next-tab', function(e){
      e.preventDefault();
      look_builder.toTabTwo($('#pub-wizard-step2'));     
    })    
    $('#pub-wizard-step1').click(function(e){
      e.preventDefault();
      var link = $(this);
      link.addClass('on').siblings('a').removeClass('on');
      $(link.attr('href')).addClass('on').siblings('div').removeClass('on');
    });
    $('#pub-wizard-step2').click(function(e){
      e.preventDefault();
      look_builder.toTabTwo($(this)); 
    });
    $('#pub-section2').on('click', 'a.next-tab', function(e){
      e.preventDefault();
      look_builder.toTabThree($('#pub-wizard-step3'));     
    })        
    $('#pub-wizard-step3').click(function(e){
      e.preventDefault();
      look_builder.toTabThree($(this));
    });
    $('#send-toggle').change(function(e){
      var box = $(this);
      var div = $('#send-later-wrapper')
      if(box.prop('checked')){
        div.show();
      }else{
        div.hide();
      }
    });
    $('#pub-section3').on('click', 'a#submit-lookbook', function(e){
      e.preventDefault();
      var lookbook = {
        styling_session_id: look_builder.session_id,
        send_at: null,
        text_content: $('#publish-email').val().replace(
          /\[Link to Lookbook\]/g, 
          '<a href="https://stage.allume.co/looks/' + $('body').data('sessiontoken') + '">Your Lookbook</a>'
        )
      }
      if($('#send-toggle').prop('checked') == true){
        var t = rome.find(document.getElementById('send-later'))
        var tz = $('#send-later').data('tz')
        var reg_str = t.getMoment().format('YYYY-MM-DD HH:MM');
        var send_string = moment.tz(reg_str, tz).format('X');
        lookbook.send_at = parseInt(send_string);
      }
      $.ajax({       
        contentType : 'application/json',
        crossDomain: true,
        data: JSON.stringify(lookbook),
        type: 'POST',
        url: 'https://styling-service-stage.allume.co/publish_looks/',
        xhrFields: {
          withCredentials: true
        }
      });
      $('#publish-lookbook-overlay').fadeOut();
    });
    /* collage funcs */
    $('#look-drop').on('click', 'a.zoom-in', function(e){
      e.preventDefault();
      collage.zoomBy(0,0,10);
    }).on('click', 'a.zoom-out', function(e){
      e.preventDefault();
      collage.zoomBy(0,0,-10);
    }).on('click', 'a.shift-left', function(e){
      e.preventDefault();
      collage.zoomBy(5,0,0);
    }).on('click', 'a.shift-right', function(e){
      e.preventDefault();
      collage.zoomBy(-5,0,0);
    }).on('click', 'a.shift-up', function(e){
      e.preventDefault();
      collage.zoomBy(0,5,0);
    }).on('click', 'a.shift-down', function(e){
      e.preventDefault();
      collage.zoomBy(0,-5,0);
    }).on('click', 'a.trash-obj', function(e){
      e.preventDefault();
      collage.trash();
    }).on('click', 'a.send-back', function(e){
      e.preventDefault();
      collage.sendBack();
    }).on('click', 'a.send-front', function(e){
      e.preventDefault();
      collage.sendForward();
    }).on('click', 'a.flip-x', function(e){
      e.preventDefault();
      collage.flipX();      
    }).on('click', 'a.crop-image', function(e){
      e.preventDefault();
      collage.setUpCrop();      
    }).on('click', 'a.bg-toggle', function(e){
      e.preventDefault();
      var link = $(this);
      var div = $('#canvas-container');
      link.toggleClass('white');
      div.toggleClass('white');   
    }).on('click','a.look-more-details', function(e){
      e.preventDefault();
      var link = $(this);
      look_builder.lookDetails(link);
    }).on('click', '#finish-editing-look', function(e){
      e.preventDefault();
      var link = $(this);
      var looks = $('#compare-looks');
      looks.find('div.comp-look.off').removeClass('off');
      var div = looks.find('div.comp-look.editing');
      collage.updateCollage(div);
      $('#look-drop').html('<div class="start">Select or add a look to edit...</div>');
      $('#publish-lookbook').data('allowed', 'false');
    });
    /* rack functionality */
    $('#rack-draggable').on('click', 'a.add', function(e){
      e.preventDefault();
      var prod = $(this);
      var data = prod.data();
      var adding = $('#adding-product').length;
      if(collage.canvas != null && adding == 0){
        $('#look-drop').append(
          '<div id="adding-product"><div class="loading-prod">' +
          '</div><span class="loading-prod-msg">adding product ' + 
          'to look...</span></div>'
        );
        collage.addCanvasImage(data.productid, data.imgsrc);
      }
    }).on('click', 'a.view', function(e){
      e.preventDefault();
      var link = $(this);
      rack_builder.inspectItem(link, 'compare');
    }).on('click', 'a.remove', function(e){
      e.preventDefault();
      var link = $(this);
      var sku = link.data('sku');
      var rack_id = link.data('rackid')
      var rack = $('#rack-list');
      var existing = rack.data('skus').split(',');
      var idx = existing.indexOf(sku);
      var arr_idx = rack_builder.rack_product_ids.indexOf(sku)
      existing.splice(idx,1);
      rack_builder.rack_product_ids.splice(arr_idx,1);
      rack.data('skus',existing.join(','));
      link.closest('div.item').remove();
      $('#rack-list').find('a.remove-from-rack[data-sku="' + sku + '"]').closest('div.item').remove();
      $.ajax({
        success:function(response){},
        type: 'DELETE',
        url: '/shopping_tool_api/rack_item/' + rack_id + '/'
      });
    }).on('click','a.close-all-rack-sections', function(e){
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
    }).on('click','a.sort-link', function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('unsort-items')){
        look_builder.unorderedRack();
      }else{
        look_builder.orderedRack();
      }
    });
    $('#cropper-btns').find('a.crop').click(function(e){
      e.preventDefault();
      collage.cropImage();
    }).end().find('a.restart').click(function(e){
      e.preventDefault();
      var data = $(this).data();
      collage.cropper.clear();
      collage.setUpCropperImage(data.path, data.prodid, 'restart');
    }).end().find('a.cancel').click(function(e){
      e.preventDefault();
      $('#crop-look-image').fadeOut();
      collage.cropper = null;
    }).end().find('a.save').click(function(e){
      e.preventDefault();
      collage.saveCrop($(this));
    });
    $('#close-crop-image').click(function(e){
      e.preventDefault();
      $('#crop-look-image').fadeOut();
      collage.cropper = null;
    })
  },
  /**
  * @description setup look builder page
  */
  init: function(){
    rack_builder.init();
    look_builder.session_id = $('body').data('stylesession');  
    look_builder.stylist_id = parseInt($('#stylist').data('stylistid'));
    /* attach the functionality */
    look_builder.functionality();
    /* set up the initial rack display */
    look_builder.unorderedRack();
    /* check if user wanted to load a look to edit at start up */
    var at_load_look = utils.readURLParams('look');
    if(at_load_look != null){
      look_builder.setUpBuilder(at_load_look);
    }
  },
  /**
  * @description view indepth product and look details
  * @param {DOM object} link - link that triggered the details view
  */
  lookDetails: function(link){
    $('#look-indepth').html(
      '<div class="indepth-loading">' +
      '<span class="pulse_loader"></span><span class="pulse_message">loading look details...</span>' +
      '</div>'
    ).fadeIn();
    $.get('/shopping_tool_api/look/' + link.data('look') + '/', function(result){
      var markup = ['<table>'];
      result.look_products.sort(function(a,b){
        if(a.layout_position > b.layout_position){ return 1}
        if(a.layout_position < b.layout_position){ return -1}
        return 0;
      });
      var cropped_images = [];
      var merchants = []
      for(var i = 0, l = result.look_products.length; i<l; i++){
        var prod = result.look_products[i];
        if(prod.product != undefined){
          var retail = prod.product.retail_price;
          var sale = prod.product.sale_price;
          var price_display = '';
          var merch = '<span class="merch">' + prod.product.merchant_name + '</span>';
          var manu = '<span class="manu">by ' + prod.product.manufacturer_name + '</span>'; 
          var fave_link = '';
          var rack_link = '';  
          merchants.push(prod.product.merchant_name); 
          if((sale >= retail)||(sale == 0)){
            price_display = '<span class="price"><em class="label">price:</em>' + 
              numeral(retail).format('$0,0.00') + '</span>';
          }else{
            price_display = '<span class="price"><em class="label">price:</em><em class="sale">(' + 
              numeral(retail).format('$0,0.00') + ')</em>' + numeral(sale).format('$0,0.00') + '</span>';
          }
          fave_link = '<a href="#" class="favorite" data-productid="' + 
            prod.product.id + '"><i class="fa fa-heart-o"></i></a>';
          var fave_idx = rack_builder.favorites_product_ids.indexOf(prod.product.id);
          if(fave_idx > -1){
            var favorite_object = rack_builder.favorites[fave_idx];
            fave_link = '<a href="#" class="favorite favorited" data-productid="' + 
            prod.product.id + '" data-faveid="' + favorite_object.id + '"><i class="fa fa-heart"></i></a>';
          }
          rack_link = '<a href="#" class="add-to-rack" data-productid="' + 
            prod.product.product_id + '"><i class="icon-hanger"></i>add to rack</a>';
          var rack_sku = prod.product.id + '_' + prod.product.merchant_id + '_' + prod.product.product_id + '_' + prod.product.sku;
          var rack_idx = rack_builder.rack_product_ids.indexOf(rack_sku);
          if(rack_idx > -1){
            rack_link = '<a href="#" class="add-to-rack selected" data-productid="' + 
              prod.product.product_id + '"><i class="fa fa-check"></i> in rack</a>';
          }
          var src = prod.product.product_image_url;
          var other_details = [];
          if(i == 0){  
            other_details.push('<td class="desc" rowspan="' + l + '"><div class="look-meta">');
            other_details.push(
              '<p class="extras"><em>stylist: </em>' + 
              result.stylist.first_name + ' ' + result.stylist.last_name + 
              '</p>'
            );
            if(result.look_style_types != undefined && result.look_style_types.length > 0){
              other_details.push('<p class="extras"><em>Style:</em> ' + 
                result.look_style_types.map(function(x, i){ return x.name}).join(', ') + 
                '</p>'
              );
            }
            if(result.look_style_occasions != undefined && result.look_style_occasions.length > 0){
              other_details.push('<p class="extras"><em>Occasions:</em> ' + 
                result.look_style_occasions.map(function(x, i){ return x.name}).join(', ') + 
                '</p>'
              );
            }      
            if(result.look_metrics[0] != undefined){
              var total_price = numeral(parseFloat(result.look_metrics[0].total_look_price)).format('$0,0.00');
              var avg_price = numeral(parseFloat(result.look_metrics[0].average_item_price)).format('$0,0.00');
              other_details.push(
                '<p class="extras"><em>Total price:</em> ' + total_price + 
                '</p><p class="extras"><em>Average item price:</em> ' + 
                avg_price + '</p>'
              );
            }
            other_details.push('<p class="desc"><em>Description:</em>' + result.description + '</p>');
            if(result.collage != null){
              other_details.push(
                '<p class="desc"><em>Collage:</em>' +
                '<img class="collage" src="' + result.collage + '"/></p>'
              );
            }
            other_details.push('</div></td>');
          }
          markup.push(
            '<tr><td class="img">' +
            '<span id="detailsitem-' + prod.id + '"><img src="' + src + '"/></span></td>' +
            '<td class="details"><a href="' + prod.product.product_url + '" target="_blank" class="name">' + 
            prod.product.product_name + '</a>' +  merch + '' + manu + '<p class="item-desc"> '+ 
            prod.product.short_product_description + '</p>' + price_display +
            '<span class="general"><em>size:</em>' + prod.product.size + '</span>' +
            '<span class="general"><em>category:</em>' + prod.product.allume_category + 
            '</span>' + fave_link + '' + rack_link + '<a href="' + prod.product.product_url + 
            '" target="_blank" class="link-to-store"><i class="fa fa-search"></i>' +
            'view at store</a></td>' + other_details.join('') + '</tr>'
          );
        }
      }
      markup.push('</table>');
      var indepth = $('#look-indepth');
      indepth.html(
        '<div class="stage"><a href="#" class="close-indepth"><i class="fa fa-times"></i></a>' +
        '<h2>' + result.name + '</h2><div class="products">' + markup.join('') + '</div></div>'
      );
      if(merchants.length > 0){
        merchants = [...new Set(merchants)];
        indepth.find('div.look-meta p.extras:first').after(
          '<p class="desc"><em>Stores:</em>' + merchants.join(', ') + '</p>'
        );
      }
      for(var i = 0, l = result.look_products.length; i<l; i++){
        var prod = result.look_products[i];
        var fave = indepth.find('a.favorite[data-productid="' + prod.product.id + '"]');
        var rack = indepth.find('a.add-to-rack[data-productid="' + prod.product.product_id + '"]');
        fave.data('details', prod.product)
        rack.data('details', prod.product)
      }
    });    
  },
  /**
  * @description helper template function to generate look markup
  * @params {object} look - the look object
  * @params {string} mod - id string modifier
  * @params {integer} check - id of currently editing look or null
  * @returns {string} HTML
  */
  lookMarkupGenerator: function(look, mod, check){
    var collage_img = '<div class="collage-placeholder">collage not yet created</div>';
    if(look.collage != null){
      collage_img = '<a href="#" class="view-look-details" data-look="' + look.id + '">' +
        '<img class="collage" src="' + look.collage + '"/></a>';
    }
    var desc = look.description != '' ? '<span class="layout desc"><em>description: </em>' + look.description + '</span>' :  '';
    var display_class = check == look.id ? 'editing' : '';
    return '<div class="comp-look ' + display_class + '" data-lookid="' + look.id + 
      '" id="client-look-id-' + look.id + '"><a href="#" class="edit-look-btn" data-lookid="' + 
      look.id + '"><i class="fa fa-pencil"></i></a><a href="#" class="delete-look-btn" data-lookid="' + 
      look.id + '"><i class="fa fa-times"></i></a><h3 class="look-name-header">' + look.name + '</h3>' +
      '<span class="layout"><em>stylist: </em>' + look.stylist.first_name + ' ' + look.stylist.last_name + '</span>' +
      '<div class="comp-look-display">' + collage_img + '</div>' + desc + 
      '<div class="editing">editing look...</div></div>';
  },
  /**
  * @description the ordered look and feel for look builder rack
  */  
  orderedRack: function(){
    var rack_items = [];
    var rack_cats = $('#rack-list div.block');
    var cat_list = $.map(rack_cats, function(c){ return $(c).data('category')})
    var faves = $('#fave-prods div.item');
    if(faves.length > 0){
      cat_list.push('Favorites');
      cat_list.sort();
    }
    if((rack_cats.length > 0)||(faves.length > 0)){
      rack_items.push(
        '<a class="close-all-rack-sections" href="#">' +
        '<i class="fa fa-caret-square-o-up"></i>collapse all sections</a>' +
        '<a class="sort-link unsort-items" href="#">' +
        '<i class="fa fa-th"></i>unsort items</a>'
      );
    }else{
      rack_items.push('<div class="empty">Your rack is empty...</div>')
    }
    var added_favorites = 0;
    $.each(rack_cats, function(idx){
      var block = $(this);
      var category = block.data('category');
      var list_idx = cat_list.indexOf(category);
      if((list_idx != idx)&&(added_favorites == 0)){
        added_favorites++;
        rack_items.push(
          '<a href="#" class="rack-section-toggle closed"><i class="fa fa-angle-right"></i>' + 
          'Favorites</a><div class="block" style="display:none" data-category="favorites">' +
          look_builder.rackFavorites(faves) + '</div>'
        );
      }
      rack_items.push(
        '<a href="#" class="rack-section-toggle"><i class="fa fa-angle-down"></i>' + 
        category + '</a><div class="block" data-category="' + category + 
        '">'
      );
      $.each(block.find('div.item'), function(index){
        var item = $(this);
        var data = item.data();
        var src = item.find('img').attr('src');
        var link = item.find('a.remove-from-rack')
        var sku = link.data('sku');
        var rack_id = link.data('rackid');
        rack_items.push(
          '<div class="item" data-productid="' + item.data('productid') + 
          '" data-url="' + src + '"><img class="handle" src="' + src + 
          '"/><a href="#"  class="add" data-productid="' + data.productid + '" data-imgsrc="' + 
          src + '"><i class="fa fa-plus circle"></i></a>' +
          '<a href="#"  class="view" data-productid="' + data.productid + 
          '"><i class="fa fa-search"></i></a>' +
          '<a href="#" class="remove" data-sku="' + sku + 
          '" data-rackid="' + rack_id + '"><i class="fa fa-times"></i></a></div>'
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
  },
  /**
  * @description helper fuction to verify user has selected at least 
  * one style and occasion for each look in lookbook
  * @returns {string} - pass/fail
  */
  publishCheck1: function(){
    var check = 0;
    var err = $('#pub-section1-errors');
    err.html('');
    $.each($('#pub-section1 div.pub-look'), function(idx){
      var div = $(this);
      var style_checks = div.find('input.style:checked').length;
      var occ_checks = div.find('input.occ:checked').length;
      if(style_checks == 0){check++;}
      if(occ_checks == 0){check++;}
    }); 
    if(check > 0){
      err.html(
        '<span><i class="fa fa-exclamation-circle"></i>' +
        'You must select at least one style and occasion ' +
        'for each look.</span>'
      );
      return 'fail';
    }else{
      return 'pass';
    }
  },
  /**
  * @description generate rack itmes for favorits
  * @param {array} faves - array of jquery items
  * @returns {string} - HTML
  */
  rackFavorites: function(faves){
    var markup = [];
    $.each(faves, function(index){
      var item = $(this);
      var data = item.data();
      var src = item.find('img').attr('src');
      markup.push(
        '<div class="item fave" data-productid="' + data.productid + 
        '" data-url="' + src + '"><span class="fave"><i class="fa fa-heart"></i></span>' +
        '<img class="handle" src="' + src + '"/>' +
        '<a href="#" class="add" data-productid="' + data.productid + '" data-imgsrc="' + 
        src + '"><i class="fa fa-plus-circle"></i></a>' +
        '<a href="#"  class="view" data-productid="' + data.productid + 
        '"><i class="fa fa-search"></i></a><a href="#" class="remove" ' +
        'data-lookitemid=""><i class="fa fa-times"></i></a></div>'
      );
    });
    return markup.join('');
  },
  /**
  * @description set up the builder ui/ux from clicked look link
  * @param {integer} id -  the look id 
  */
  setUpBuilder: function(id){
    $('#look-drop').html('<div class="start">building look editor...</div>');
    /* get the look settings to build the drop zone */
    $.get('/shopping_tool_api/look/' + id + '/', function(result){
      $('#creating-look').hide();
      if(result.allume_styling_session == look_builder.session_id){
        $('#look-drop').html(
          '<div id="canvas-container">' +
          '<canvas id="c" width="760" height="415"></canvas>' +
          '</div><div class="collage-controls">'+
          '<a href="#" id="finish-editing-look" data-lookid="' + id + 
          '"><i class="fa fa-check"></i>finished editing look</a>' +
          '<a class="bg-toggle checker-bg" data-balloon="toggle collage ' +
          'background" data-balloon-pos="up" href="#"><em></em></a>' +
          '<a class="zoom-in" data-balloon="zoom in" data-balloon-pos="up" href="#">' +
          '<i class="fa fa-search-plus"></i></a>' +
          '<a class="zoom-out" data-balloon="zoom out" data-balloon-pos="up" href="#">' +
          '<i class="fa fa-search-minus"></i></a>' +
          '<a class="flip-x" data-balloon="flip horizontal" data-balloon-pos="up" href="#">' +
          '<i class="fa fa-refresh"></i></a>' +
          '<a class="shift-left" data-balloon="shift left" data-balloon-pos="up" href="#">' +
          '<i class="fa fa-chevron-left"></i></a>' +
          '<a class="shift-up" data-balloon="shift up" data-balloon-pos="up" href="#">' +
          '<i class="fa fa-chevron-up"></i></a>' +
          '<a class="shift-down" data-balloon="shift down" data-balloon-pos="up" href="#">' +
          '<i class="fa fa-chevron-down"></i></a>' +
          '<a class="shift-right" data-balloon="shift right" data-balloon-pos="up" href="#">' +
          '<i class="fa fa-chevron-right"></i></a>' +
          '<a href="#" data-balloon="move to back" data-balloon-pos="up" class="send-back">' +
          '<i class="fa fa-reply"></i></a>' +
          '<a href="#" data-balloon="move to front" data-balloon-pos="up" class="send-front">' +
          '<i class="fa fa-share"></i></a>' +
          '<a href="#" data-balloon="crop image" data-balloon-pos="up" class="crop-image">' +
          '<i class="fa fa-crop"></i></a>' +
          '<a href="#" class="trash-obj" data-balloon="remove product" data-balloon-pos="up">' +
          '<i class="fa fa-trash"></i></a></div>' +
          '<span class="collage-sep"></span>' +
          '<table class="collage-meta-fields"><tr><td>' +
          '<label>Name</label><input id="look-name" value="' + 
          result.name + '"/><label>Description</label><textarea id="look-desc">' + 
          result.description + '</textarea></td><td><label>Additional Products</label>' +
          '<div id="non-collage-items"></div><a href="#" class="look-more-details" data-look="' + id + 
          '"><i class="fa fa-search"></i>view more details about this look</a></td></tr></table>' +
          '<input type="hidden" id="look-id" value="' + id + '"/>'
        );
        collage.collageSortable = null;
        collage.collageSortable = new Sortable($('#canvas-container')[0], {
          group: { name: "look", pull: false, put: true },
          sort: false,
          onAdd: function (evt) {
            var el = evt.item;
            var adding = $('#adding-product').length;
            if(adding == 0){
             $('#look-drop').append(
                '<div id="adding-product"><div class="loading-prod">' +
                '</div><span class="loading-prod-msg">adding product ' + 
                'to look...</span></div>'
              );            
              collage.addCanvasImage(el.dataset.productid, el.dataset.url);
            }
            el.parentNode.removeChild(el);
          }
        });
        new Sortable($('#non-collage-items')[0], {
          group: { name: "look", pull: false, put: true },
          sort: false,
          onAdd: function (evt) {
            var item = $(evt.item)
            var data = evt.item.dataset;
            var look_product_obj = {
              layout_position: 100,
              look: parseInt($('input#look-id').val()),
              product: parseInt(data.productid),
              cropped_dimensions: null,
              in_collage: 'False',
              cropped_image_code: null      
            }
            $.ajax({
              contentType : 'application/json',
              data: JSON.stringify(look_product_obj),
              success:function(response){
                item.find('a.remove').data('lookitemid', response.id)
                collage.addAllumeProduct(response.product, response.id);
              },
              type: 'PUT',
              url: '/shopping_tool_api/look_item/0/'
            });
          }
        });
        $('#non-collage-items').on('click', 'a.remove', function(e){
          e.preventDefault();
          var link = $(this);
          var lookitm = link.data('lookitemid');
          link.closest('div.item').remove();
          $.ajax({
            success:function(response){},
            type: 'DELETE',
            url: '/shopping_tool_api/look_item/' + lookitm + '/'
          });
        })
        $('#canvas-container').mousedown(function(){
          collage.collageSortable.option("disabled", true);
        })
        result.look_products.sort(function(a,b){
          if(a.layout_position < b.layout_position){ return 1}
          if(a.layout_position > b.layout_position){ return -1}
          return 0;
        })        
        collage.init(result.look_products);
      }
    });
  },
  /**
  * @description the unordered look and feel for look builder rack
  */
  unorderedRack: function(){
    var rack_items = [];
    var rack_items_dom = $('#rack-list').find('div.item');
    if(rack_items_dom.length > 0){
      rack_items.push(
        '<a class="sort-link sort-items" href="#">' +
        '<i class="fa fa-th-list"></i>sort items</a>'
      );
    }else{
      rack_items.push('<div class="empty">Your rack is empty...</div>');
    }
    $.each(rack_items_dom, function(index){
      var item = $(this);
      var data = item.data();
      var src = item.find('img').attr('src');
      var link = item.find('a.remove-from-rack')
      var sku = link.data('sku');
      var rack_id = link.data('rackid');
      rack_items.push(
        '<div class="item" data-productid="' + data.productid + 
        '" data-url="' + src + '"><img class="handle" src="' + src + 
        '"/><a href="#" class="add" data-productid="' + data.productid + '" data-imgsrc="' + 
        src + '"><i class="fa fa-plus-circle"></i></a>' +
        '<a href="#"  class="view" data-productid="' + data.productid + 
        '"><i class="fa fa-search"></i></a>' +
        '<a href="#" class="remove" data-sku="' + sku + 
        '" data-rackid="' + rack_id + '"><i class="fa fa-times"></i></a></div>'
      );
    });
    var faves = $('#fave-prods div.item');
    if(faves.length > 0){
      rack_items.push(look_builder.rackFavorites(faves));
    }
    /* add the clones and assign drag/drop functionality */
    var drag_rack = $('#rack-draggable');
    drag_rack.html(
      '<h2>' + $('#rack').find('h2').html() + 
      '</h2><div class="look-builder-rack">' + 
      rack_items.join('') + '</div>'
    );
    new Sortable($('#rack-draggable div.look-builder-rack')[0], {
      handle: ".handle",
      group: { name: "look", pull: 'clone', put: false },
      sort: true,
      draggable: ".item",
      onStart: function(){
        var cc = $('#canvas-container');
        if(cc.length > 0){
          collage.collageSortable.option('disabled', false);
        }
      }
    });  
  },
  /**
  * @description switching to tab two in publish look book flow
  * @param {DOM Object} link - the link that trigger the navigation
  */
  toTabTwo: function(link) {
    var loading_check = $('#pub-section1 div.publish-loading').length;
    if(loading_check == 0){
      var step = look_builder.publishCheck1();
      if(step == 'pass'){
        link.addClass('on').siblings('a').removeClass('on');
        $(link.attr('href')).addClass('on').siblings('div').removeClass('on');
        look_builder.updateLookCategories();
      }
    } 
  },
  /**
  * @description switching to tab three in publish look book flow
  * @param {DOM Object} link - the link that trigger the navigation
  */  
  toTabThree: function(link){
    var loading_check = $('#pub-section1 div.publish-loading').length;
    if(loading_check == 0){
      var step = look_builder.publishCheck1();
      if(step == 'pass'){
        look_builder.updateLookCategories();
        var look_summary = [];
        $.each($('#pub-section1 div.pub-look'), function(idx){
          var div = $(this);
          var styles = [];
          var occs = [];
          $.each(div.find('input.style:checked'), function(num){
            styles.push($(this).data('display'));
          });
          $.each(div.find('input.occ:checked'), function(num){
            occs.push($(this).data('display'));
          });
          look_summary.push(
            '<div class="look-summary"><span class="name">' + div.data('lookname') + 
            '</span><span class="categories"><em>style:</em>' + styles.join(', ') + 
            '</span><span class="categories"><em>occasion:</em>' + occs.join(', ') + 
            '</span></div>'
          )
        });
        var step_div = $(link.attr('href'));
        var email_at = '<span class="summary-sent">Text will be sent <strong>now</strong>.</span>';
        if($('#send-toggle').prop('checked')){
          var t = rome.find(document.getElementById('send-later'))
          email_at = '<span class="summary-sent">Text will be sent <strong>' + 
          t.getMoment().format('MMMM Do, YYYY h:mm a') + 
          ' ' + $('#send-later').data('tz') + '</strong> time zone</span>';
        }
        var email_text = $('#publish-email').val();
        email_text = email_text.replace(
          /\[Link to Lookbook\]/g, 
          '<a href="https://stage.allume.co/looks/' + $('body').data('sessiontoken') +
          '" target="_blank">Your Lookbook</a>'
        );

        step_div.html(
          '<h5>Looks</h5><div class="look-summary-section">' +
          look_summary.join('') + '</div>' +
          '<h5>Text</h5>' + email_at +
          '<div class="summary-email">' + email_text +
          '</div><a href="#" id="submit-lookbook">complete publishing</a>' 
        );
        link.addClass('on').siblings('a').removeClass('on');
        step_div.addClass('on').siblings('div').removeClass('on');
      }
    }    
  },
  /**
  * @description update a look with any changes to its fields
  * @param {DOM Object} div - div to be updated with new display
  * @param {integer} look_id - id of the look to update
  * @param {string} look_name - look name
  * @param {string} look_desc - look description
  */
  updateLook: function(div, look_id, look_name, look_desc){
    /* before we can update the look we need to add the watermark to the collage */
    var img = new Image(); 
    /* watermarl path */
    img.src = '/static/shopping_tool/image/allume_watermark.png';
    img.onload = function() {
      /* scale: 0.15, left: 657, and top: 393 based upon 1365 x 284 watermark dimensions */
      var scale = 0.15;
      var fImg = new fabric.Cropzoomimage(this, {
        originX: 'center',
        originY: 'center',
        left: 657,
        top: 393,
        scaleX: scale,
        scaleY: scale,
        prod_id: 'watermark'
      });
      collage.canvas.add(fImg);
      /* since we are saving as high quality jpeg we need to set the canvas bg to white */
      collage.canvas.backgroundColor = '#ffffff';
      /* set the watermark as unselectable so we don;t get the outline in the jpeg */
      fImg.selectable = false;
      collage.canvas.setActiveObject(fImg);
      /* call render all to pick up new background */
      collage.canvas.renderAll();
      /* get base64 jpeg of canvas */
      var src = collage.canvas.toDataURL({
        format: 'jpeg',
        quality: 1,
      });
      /* the look object to save */
      var look_obj = {
        "name": look_name,
        "description": look_desc,
        "allume_styling_session": look_builder.session_id,
        "stylist": look_builder.stylist_id,
        "collage": src
      }
      /* update the look with the new values */
      $.ajax({
        contentType : 'application/json',
        data: JSON.stringify(look_obj),
        success:function(response){
          $.get('/shopping_tool_api/look/' + look_id + '/', function(result){
            div.before(look_builder.lookMarkupGenerator(result, 'comp', null));
            div.remove();
          });
        },
        type: 'PUT',
        url: '/shopping_tool_api/look/' + look_id + '/'
      });
      /* reset the collage cache holders so collage is ready for new look to edit */
      collage.canvas = null;
      collage.initial_load = null;
      collage.product_cache = null;      
    }     
  },
  /**
  * @description update looks categories when tabs are clicked in publish
  */  
  updateLookCategories: function(){
    $.each($('#pub-section1 div.pub-look'), function(idx){
      var div = $(this);
      var data = div.data();
      var look = {
        look_id: data.lookid,
        style_type: [],
        style_occasion: []
      }
      $.each(div.find('input.style:checked'), function(num){
        look.style_type.push(parseInt($(this).val()));
      });
      $.each(div.find('input.occ:checked'), function(num){
        look.style_occasion.push(parseInt($(this).val()));
      });
      $.ajax({
        contentType : 'application/json',
        data: JSON.stringify(look),
        success:function(response){console.log(response)},
        type: 'PUT',
        url: '/shopping_tool_api/look_meta_tags/' + data.lookid + '/'
      });
    });
  }
}