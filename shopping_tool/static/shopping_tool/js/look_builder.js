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
  editableLooksMarkup: function(lookup, at_load){
    var at_load_look = utils.readURLParams('look');
    var comp_looks = $('#compare-looks div.other-looks');
    $.ajax({
      contentType : 'application/json',
      data: JSON.stringify(lookup),
      success:function(response){
        var markup = [];
        var cropped_images = [];
        for(var i = 0, l = response.looks.length; i<l; i++){
          var comp = response.looks[i];
          var content = look_builder.lookMarkupGenerator(comp, 'comp', at_load)
          markup.push(content[0]);
          cropped_images = cropped_images.concat(content[1]);
        }
        /* display no looks message or add looks and drag/drop functionality */
        if(markup.length == 0){ 
          comp_looks.html('<span class="no-looks">add some looks...</span>'); 
        }else if(markup.length > 0){
          comp_looks.html(markup.join(''));
          if(at_load != null){
            $('#compare-looks div.comp-look:not(".editing")').addClass('off');
          }
          /* afix cropped images if present */
          if(cropped_images.length > 0){
            for(var i = 0, l = cropped_images.length; i<l; i++){
              look_builder.getCroppedImage(cropped_images[i], '#compare-looks');
            }
          }
        }
      },
      type: 'POST',
      url: '/shopping_tool_api/look_list/'
    });
  },
  /** 
  * @description create the crop image ui/ux
  * @param {DOM object} link - a element that triggered the crop initiation
  */
  cropImage: function(link){
    var data = link.data();
    var crop_dim = data.crop != null ? data.crop.split(',') : [];
    var start_size = [50,50, '%'];
    if(crop_dim[0] != undefined){
      start_size = [crop_dim[0], crop_dim[1], 'px']
    }
    var work_station = $('#cropper-zone');
    work_station.html(
      '<p>Crop the product image to your desired dimensions. You will ' +
      'see a live preview to the right. When happy hit the save crop button.</p>' +
      '<img id="image-to-crop" src="' + look_proxy + '' + link.data('url') + '"/>' +
      '<div id="thumb"><h6>crop preview</h6></div>'
    );
    var img  = $('#image-to-crop');
    var display_w = $('#cropper-zone').width();
    $('#cropper').fadeIn(function(){
      var imgObject = new Image();
      imgObject.src = look_proxy + '' +link.data('url');
      var croppr = new Croppr('#image-to-crop', {
        startSize: start_size,
        onUpdate: function(value) {
          var newImg = look_builder.getImagePortion(imgObject, value.width, value.height, value.x, value.y, 1);
          /* place image in appropriate div */
          $('#thumb').html(
            '<h6>crop preview</h6>' +
            '<img alt="" src="' +newImg+ '"/>' +
            '<a href="#" class="save-crop" data-look="' + data.look + 
            '" data-productid="' + data.productid + '" data-lookitemid="'+
            data.lookitemid + '" data-position="' + data.position + '" data-crop="' + 
            value.width + ',' + value.height + ',' +  value.x + ',' + value.y + '">save crop</a>'
          );
        },
      });
      if(crop_dim[0] != undefined){
        croppr.moveTo(parseInt(crop_dim[2]),parseInt(crop_dim[3]));
      }
    });
  },
  /**
  * @description look builder ui/ux functionality
  */
  functionality: function(){
    $('#preview-lookbook').click(function(e){
      e.preventDefault();
    });
    $('#publish-lookbook').click(function(e){
      e.preventDefault();
    });
    $('#add-new-look-to-lookbook').click(function(e){
      e.preventDefault();
      $('#new-look-error').html('');
      $('#new-look-name').val('');
      $('#new-look-layout')[0].selectize.setValue('',true);
      $('#create-look').fadeIn();
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
          /* create look option grid display */
          var markup = ['<div class="grid-display-wrapper"><div class="grid-skew">'];
          for(var i = 0, l = item.display.length; i<l; i++){
            var block = item.display[i];
            markup.push(
              '<span class="layout-block" style="height:' + (block.height - 2) + 'px;' +
              'width:' + (block.width - 2) + 'px;top:' + block.y + 'px;left:' + block.x + 
              'px"></span>'
            )
          }
          markup.push('</div></div>');
          return '<div class="layout-option">' +
            '<div class="layout-grid">' + markup.join('')+ '</div>' +
            '<span class="name">' + escape(item.name) + '</span>' +
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
       "description": '',
       "allume_styling_session": look_builder.session_id,
       "stylist": look_builder.stylist_id        
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
        $('#creating-look').show();
        $('#create-look').hide();
        $.ajax({
          contentType : 'application/json',
          data: JSON.stringify(look_obj),
          success:function(response){
            look_builder.setUpBuilder(response.id);
            $.get('/shopping_tool_api/look/' + response.id + '/', function(result){
              var content = look_builder.lookMarkupGenerator(result, 'comp', null);
              $('#compare-looks div.other-looks').prepend(content[0]);
              var new_div = $('#compare-looks div.other-looks div.comp-look:nth-child(1)');
              new_div.addClass('editing').siblings('div.comp-look').removeClass('editing off').addClass('off')
            });
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
    }).on('click','a.sort-link', function(e){
      e.preventDefault();
      var link = $(this);
      if(link.hasClass('unsort-items')){
        look_builder.unorderedRack();
      }else{
        look_builder.orderedRack();
      }
    });
    $('#fave-looks').on('click', 'a.item-detail', function(e){
      e.preventDefault();
      var link = $(this);
      rack_builder.inspectItem(link, 'compare');
    })
    $('#looks-list').on('click', 'a.item-detail', function(e){
      e.preventDefault();
      var link = $(this);
      rack_builder.inspectItem(link, 'compare');
    });

    $('#look-drop').on('click','a.look-more-details', function(e){
      e.preventDefault();
      var link = $(this);
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
        for(var i = 0, l = result.look_products.length; i<l; i++){
          var prod = result.look_products[i];
          if(prod.product != undefined){
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
            var src = prod.product.product_image_url;
            /* if product has been cropped for the look add crop object */
            if(prod.cropped_dimensions != null){
              var crop = {
                id: 'detailsitem-' + prod.id,
                src: look_proxy + '' + src,
                dims: prod.cropped_dimensions
              }
              cropped_images.push(crop);
            }
            var other_details = '';
            if(i == 0){
              other_details = '<td class="desc" rowspan="' + l + '"><p class="desc"><em>description:</em>' + 
                result.description + '</td>';
            }
            markup.push(
              '<tr><td class="img"><a href="#" class="crop-product-image" data-productid="' + prod.product.id + 
              '" data-url="' + prod.product.product_image_url  + '" data-look="' + result.id + 
              '" data-lookitemid="' + prod.id + '" data-position="' + prod.layout_position + 
              '" data-crop="' + prod.cropped_dimensions + '"><i class="fa fa-crop"></i></a>' +
              '<span id="detailsitem-' + prod.id + '"><img src="' + src + '"/></span></td>' +
              '<td class="details"><a href="' + prod.product.product_url + '" target="_blank" class="name">' + 
              prod.product.product_name + '</a>' +  merch + '' + manu + '<p class="item-desc"> '+ 
              prod.product.short_product_description + '</p>' + price_display +
              '<span class="general"><em>size:</em>' + prod.product.size + '</span>' +
              '<span class="general"><em>category:</em>' + prod.product.primary_category + 
              '</span></td>' + other_details + '</tr>'
            );
          }
        }
        markup.push('</table>');
        $('#look-indepth').html(
          '<div class="stage"><a href="#" class="close-indepth"><i class="fa fa-times"></i></a>' +
          '<h2>' + result.name + '</h2><p class="layout">' +
          '<a href="https://shopping-tool-web-stage.allume.co/collage_image/' + result.id + 
          '.jpg" id="collage-preview" target="_blank">preview collage</a>' +
          '<em>layout: </em>' + result.look_layout.display_name + 
          '</p><div class="products">' + markup.join('') + '</div></div>'
        );
        if(cropped_images.length > 0){
          for(var i = 0, l = cropped_images.length; i<l; i++){
            look_builder.getCroppedImage(cropped_images[i], '#look-indepth');
          }
        }
      });
    }).on('click','a.crop-product-image',function(e){
      e.preventDefault();
      var link = $(this);
      look_builder.cropImage(link);
    }).on('blur', 'input#look-name', function(e){
      look_builder.updateLook();
    }).on('blur', 'textarea#look-desc', function(e){
      look_builder.updateLook();
    }).on('click', '#finish-editing-look', function(e){
      e.preventDefault();
      var link = $(this);
      var data = link.data();
      var looks = $('#compare-looks');
      looks.find('div.comp-look.off').removeClass('off');
      var div = looks.find('div.comp-look.editing');
      div.addClass('updating').removeClass('editing').find('div.editing').html('loading changes...');
      $.get('/shopping_tool_api/look/' + data.lookid + '/', function(result){
        var content = look_builder.lookMarkupGenerator(result, 'comp', null);
        div.before(content[0]);
        div.remove();
        if(content[1].length > 0){
          for(var i = 0, l = content[1].length; i<l; i++){
            look_builder.getCroppedImage(content[1][i], '#compare-looks');
          }
        }
      });
      $('#look-drop').html('<div class="start">Select or add a look to edit...</div>');
    });
    $('#compare-looks').on('click', 'a.item-detail', function(e){
      e.preventDefault();
      var link = $(this);
      rack_builder.inspectItem(link, 'compare');
    }).on('click', 'a.edit-look-btn', function(e){
      e.preventDefault();
      var link = $(this);
      var look = link.data('lookid');
      var div = link.closest('div.comp-look');
      div.addClass('editing').siblings('div.comp-look').removeClass('editing').addClass('off');
      look_builder.setUpBuilder(look);
    });
    $('#look-indepth').on('click', 'a.close-indepth', function(e){
      e.preventDefault();
      $('#look-indepth').fadeOut();
    }).on('click','a.crop-product-image',function(e){
      e.preventDefault();
      var link = $(this);
      look_builder.cropImage(link);
    });
    $('#cropper').on('click','a.save-crop',function(e){
      e.preventDefault();
      var link = $(this);
      var data = link.data();
      /* set up update object with correct/new values */
      var update_json = {
        "id": data.lookitemid,
        "layout_position": data.position,
        "look": data.look,
        "product": data.productid,
        "cropped_dimensions": data.crop
      }
      /* update the look item */
      $.ajax({
        contentType : 'application/json',
        data: JSON.stringify(update_json),
        success:function(response){
          $('#look-indepth').fadeOut();
          $('#cropper').fadeOut();
          /* redraw look builder do we pick up the new crop */
          look_builder.setUpBuilder(data.look);
        },
        type: 'PUT',
        url: '/shopping_tool_api/look_item/' + data.lookitemid + '/'
      })
    });
    $('#close-cropper').click(function(e){
      e.preventDefault();
      $('#cropper').fadeOut();
    });
    $('#publish-lookbook').click(function(e){
      e.preventDefault();
      $('#publish-lookbook-overlay').fadeIn();
      /* the setting looks categories go here */
    });
    $('#close-lb').click(function(e){
      e.preventDefault();
      $('#publish-lookbook-overlay').fadeOut();
    });    
  },
  /**
  * @description to handle invalid states we use a recursive loading check for images before we crop them
  * @param {object} crop - object containing the image attributes we need to send top cropper function
  * @param {string} selectore - css selector used to update the correct item with new cropped image
  */
  getCroppedImage: function(crop, selector){
    var loadTimer;
    var imgObject = new Image();
    imgObject.src = crop.src;          
    imgObject.onLoad = onImgLoaded();
    function onImgLoaded() {
      if (loadTimer != null){ clearTimeout(loadTimer); };
      if (!imgObject.complete) {
        loadTimer = setTimeout(function() {
          onImgLoaded();
        }, 3);
      } else {
        var dims = crop.dims.split(',')
        var new_src = look_builder.getImagePortion(imgObject, dims[0],dims[1],dims[2], dims[3], 1);
        var dom = $(selector + ' #' + crop.id);
        var img_h = dom.find('img').height()
        dom.find('img').attr('src', new_src );
      }
    }
  },
  /**
  * @description take and image and apply user provided crop coordinates and return new image via HTML5 canvas
  * @param {object} imgObj - the image to be used for cropping
  * @param {integer} newWidth - the new width
  * @param {integer} newHeight - the new height
  * @param {integer} startX - X coordinates to begin the crop
  * @param {integer} startY - Y coordinates to begin crop
  * @param {integer} ratio - aspect ratio to apply to the crop
  * @returns {string} data url of new image
  */ 
  getImagePortion: function(imgObj, newWidth, newHeight, startX, startY, ratio){
    /* set up canvas for thumbnail */
    var tnCanvas = document.createElement('canvas');
    var tnCanvasContext = tnCanvas.getContext('2d');
    tnCanvas.width = newWidth; tnCanvas.height = newHeight;
    /* use the sourceCanvas to duplicate the entire image. */
    var bufferCanvas = document.createElement('canvas');
    var bufferContext = bufferCanvas.getContext('2d');
    bufferCanvas.width = imgObj.width;
    bufferCanvas.height = imgObj.height;
    bufferContext.drawImage(imgObj, 0, 0);
    /* now we use the drawImage method to take the pixels from our bufferCanvas and draw them into our thumbnail canvas */
    tnCanvasContext.drawImage(bufferCanvas, startX, startY, newWidth * ratio, newHeight * ratio, 0, 0, newWidth, newHeight);
    var img_data = tnCanvas.toDataURL();
    $('canvas').remove();
    return img_data
  },
  /**
  * @description setup look builder page
  */
  init: function(){
    utils.menu();
    utils.client();
    rack_builder.init();
    /* cache ids for faster reuse */
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
    /* build list of session looks */
    var lookup = {
      "client": parseInt($('#user-clip').data('userid')),
      "allume_styling_session": look_builder.session_id,
      "stylist": look_builder.stylist_id,
      "page": 1
    }
    look_builder.editableLooksMarkup(lookup, at_load_look);
  },
  /**
  * @description helper template function to generate look markup
  * @params {object} look - the look object
  * @params {string} mod - id string modifier
  * @params {integer} check - id of currently editing look or null
  * @returns {array}  - [HTML, cropped images array]
  */
  lookMarkupGenerator: function(look, mod, check){
      var look_products_markup = ['<div class="compare-look-wrapper"><div class="compare-looks-layout">'];
      var cropped_images = [];
      for(var ix = 0, lx = look.look_layout.layout_json.length; ix<lx; ix++){
        var block = look.look_layout.layout_json[ix];
        var position = block.position;
        var product_markup = [];
        for(var p = 0, prods = look.look_products.length; p<prods; p++){
          var prod = look.look_products[p];
          if((prod.layout_position == position)&&(prod.product != undefined)){
            var src = prod.product.product_image_url;
            if(prod.cropped_dimensions != null){
              var crop = {
                id: mod + '-' + look.id + '-item-' + prod.id,
                src: look_proxy + '' + src,
                dims: prod.cropped_dimensions
              }
              cropped_images.push(crop);
            }
            product_markup.push(
              '<div class="item"><a href="#" class="item-detail" ' + 
                'data-name="' + prod.product.product_name + '" data-brand="' + prod.product.manufacturer_name + 
                '" data-productid="' + prod.product.id + '"><span id="' + mod + '-' + look.id + '-item-' + prod.id + 
                '"><img style="height:' + block.height + 'px" src="' + src + '"/></span></a></div>'
            );
          }
        }
        look_products_markup.push(
          '<div class="layout-block" style="height:' + (block.height - 4) + 'px;' +
          'width:' + (block.width - 4) + 'px;top:' + block.y + 'px;left:' + block.x + 
          'px" data-position="' + position + '">' + product_markup.join() + '</div>'
        );
      }
      look_products_markup.push('</div></div>');
      var desc = look.description != '' ? '<span class="layout desc"><em>description: </em>' + look.description + '</span>' :  '';
      var display_class = check == look.id ? 'editing' : '';
      return ['<div class="comp-look ' + display_class + '" data-lookid="' + look.id + 
        '"><a href="#" class="edit-look-btn" data-lookid="' + 
        look.id + '"><i class="fa fa-pencil"></i></a><h3>' + look.name + '</h3>' +
        '<span class="layout"><em>layout: </em>' + look.look_layout.display_name + '</span>' +
        '<div class="comp-look-display">' + look_products_markup.join('') + '</div>' + desc + 
        '<div class="editing">editing look...</div></div>', cropped_images];
  },
  /**
  * @description the ordered look and feel for look builder rack
  */  
  orderedRack: function(){
    var rack_items = [];
    var rack_cats = $('#rack-list div.block');
    if(rack_cats.length > 0){
      rack_items.push(
        '<a class="close-all-rack-sections" href="#">' +
        '<i class="fa fa-caret-square-o-up"></i>collapse all sections</a>' +
        '<a class="sort-link unsort-items" href="#">' +
        '<i class="fa fa-th"></i>unsort items</a>'
      );
    }else{
      rack_items.push('<div class="empty">Your rack is empty...</div>')
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
        var src = item.find('img').attr('src');
        rack_items.push(
          '<div class="item" data-productid="' + item.data('productid') + 
          '" data-url="' + src + '"><img class="handle" src="' + src + '"/></div>'
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
      if((result.allume_styling_session == look_builder.session_id)&&(result.stylist == look_builder.stylist_id)){
        var look_drop = $('#look-drop');
        var cropped_images = [];
        var markup = [];
        markup.push('<div id="look-layout-grid">')
        for(var i = 0, l = result.look_layout.layout_json.length; i<l; i++){
          var block = result.look_layout.layout_json[i];
          var position = block.position;
          var product_markup = [];
          for(var p = 0, prods = result.look_products.length; p<prods; p++){
            var prod = result.look_products[p];
            if((prod.layout_position == position)&&(prod.product != undefined)){
              var src = prod.product.product_image_url;
              if(prod.cropped_dimensions != null){
                var crop = {
                  id: 'lookitem-' + prod.id,
                  src: look_proxy + '' + src,
                  dims: prod.cropped_dimensions
                }
                cropped_images.push(crop);
              }
              product_markup.push(
                '<div class="item" id="lookitem-' + prod.id + 
                '" data-productid="' + prod.product.id + 
                '" data-lookitemid="' + prod.id + '">' +
                '<a href="#" class="crop-product-image" data-productid="' + prod.product.id + 
                '" data-url="' + prod.product.product_image_url  + '" data-look="' + result.id + 
                '" data-lookitemid="' + prod.id + '" data-position="' + prod.layout_position + 
                '" data-crop="' + prod.cropped_dimensions + '"><i class="fa fa-crop"></i></a>' +
                '<img class="handle" src="' + src + '"/></div>'
              );
            }
          }
          markup.push(
            '<div class="layout-block" style="height:' + (block.height - 4) + 'px;' +
            'width:' + (block.width - 4) + 'px;top:' + block.y + 'px;left:' + block.x + 
            'px" data-position="' + position + '">' + product_markup.join() + '</div>'
          );
        }
        markup.push('</div>');
        /* add the created look markup to the ui, including instructions and trash bin */
        look_drop.html(
          '<a href="#" class="look-more-details" data-look="' + id + '">' +
          '<i class="fa fa-search"></i>look details</a>' +
          '<p class="look-drop-info">&bull; Drag items from the left into ' +
          'the look layout, or items from the look to trash to remove.</p>' + markup.join('') + 
          '<div id="look-trash"></div><label style="margin-top:10px">Name</label><input id="look-name" value="' + 
          result.name + '"/><label>Description</label><textarea id="look-desc">' + 
          result.description + '</textarea><input type="hidden" id="look-layoutid" value="' + 
          result.look_layout.id + '"/><input type="hidden" id="look-id" value="' + id + '"/>' +
          '<a href="#" id="finish-editing-look" data-lookid="' + id + '"><i class="fa fa-check"></i>done editing</a>'
        );
        if(cropped_images.length > 0){
          for(var i = 0, l = cropped_images.length; i<l; i++){
            look_builder.getCroppedImage(cropped_images[i], '#look-layout-grid');
          }
        }
        /* add the trash functionality - simply accept objects and immediately remove from ui */
        new Sortable(document.getElementById('look-trash'), {
          group: "look",
          onAdd: function (evt) {
            var el = evt.item;
            el.parentNode.removeChild(el);
          }
        });
        /* add the drag/drop functionality to the newly created drop zones */
        $.each(look_drop.find('#look-layout-grid div.layout-block'), function(idx){
          var box = $(this);
          new Sortable(box[0], {
            handle: ".handle",
            group: { name: "look", pull: true, put: true },
            sort: false,
            draggable: ".item",
            onAdd: function (evt) {
              var el = evt.item;
              var el_id = el.dataset.productid;
              /* create REST object */
              var obj = {
                layout_position: box.data('position'),
                look: id,
                product: parseInt(el_id),
                cropped_dimensions:  null         
              }
              var dims = $(el).find('a.crop-product-image').data('crop')
              if(dims != null){
                obj.cropped_dimensions = dims;
              }
              $.ajax({
                contentType : 'application/json',
                data: JSON.stringify(obj),
                success:function(response){
                  var elem = $(el);
                  elem.data('lookitemid', response.id)
                  elem.data('isnew', 'yes');
                  elem.siblings('div.item').data('isnew','no')
                  if(elem.find('a.crop-product-image').length == 0){
                    elem.append(
                      '<a href="#" class="crop-product-image" data-productid="' + response.product + 
                      '" data-url="' + elem.data('url')  + '" data-look="' + response.look + 
                      '" data-lookitemid="' + response.id + '" data-position="' + response.layout_position + 
                      '" data-crop="' + response.cropped_dimensions + '"><i class="fa fa-crop"></i></a>'
                    );
                  }
                  /** ecom API addition */
                  $.ajax({
                    data: 'look_product_id=' + response.id,
                    type: 'POST',
                    url: 'https://ecommerce-service-stage.allume.co/wp-json/products/create_or_update_client_products_and_link_to_look/'
                  });
                  var list_items = box.find('div.item');
                  if(list_items.length > 1){
                    $.each(list_items, function(e){
                      var item = $(this);
                      var data = item.data();
                      if(data.isnew == 'no'){
                        $.ajax({
                          success:function(response){
                            item.remove();
                          },
                          type: 'DELETE',
                          url: '/shopping_tool_api/look_item/' + data.lookitemid + '/'
                        });
                      }
                    });
                  }
                },
                type: 'PUT',
                url: '/shopping_tool_api/look_item/0/'
              });
            },
            onRemove: function(evt){
              var elem = $(evt.item);
              /* delete the item from the look/db when removed from a drop box */
              $.ajax({
                success:function(response){},
                type: 'DELETE',
                url: '/shopping_tool_api/look_item/' + elem.data('lookitemid') + '/'
              });            
            }
          });        
        });
      }else{

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
      var src = item.find('img').attr('src');
      rack_items.push(
        '<div class="item" data-productid="' + item.data('productid') + 
        '" data-url="' + src + '"><img class="handle" src="' + src + '"/></div>'
      );
    });
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
      draggable: ".item"
    });  
  },
  /**
  * @description update a look with any changes to its fields
  */
  updateLook: function(){
    var look_obj = {
     "name": $('#look-name').val(),
     "look_layout": parseInt($('input#look-layoutid').val()),
     "description": $('#look-desc').val(),
     "allume_styling_session": look_builder.session_id,
     "stylist": look_builder.stylist_id        
    }
    $.ajax({
      contentType : 'application/json',
      data: JSON.stringify(look_obj),
      success:function(response){},
      type: 'PUT',
      url: '/shopping_tool_api/look/' + $('input#look-id').val() + '/'
    });  
  }
}