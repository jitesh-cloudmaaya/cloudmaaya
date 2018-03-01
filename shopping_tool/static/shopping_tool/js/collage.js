/**
* @description collage namespace for collage builder
*/
var collage = {
  /**
  * @description function to create and submit newly added look products to the allum db
  * @param {integer} product_id - the id of the product being added
  * @param {integer} look_item_id - the app look item id
  */
  addAllumeProduct: function(product_id, look_item_id){
    console.log('firing addAllumeProduct')
    $.ajax({
      success: function(results){
        if((results.data != undefined)&&(results.data.length > 0)){
          var payload = {sites: { } };
          var tmp = {color_names: [], color_objects: {}};
          var matching_object = '';
          /* loop through results to set up content for payload */
          for(var i = 0, l = results.data.length; i<l; i++){
            var product = results.data[i]._source;
            if((product.id == product_id)||(product.product_id == product_id)){
              matching_object = product;
            }
            /* create color object for payload */
            var clr = product.color.toLowerCase();
            if(tmp.color_names.indexOf(clr) == -1){
              tmp.color_names.push(clr);
              tmp.color_objects[clr] = { sizes: [], size_data : {}};
            }
            var all_sizes = product.size.split(',')
            for(var ix = 0, lx = all_sizes.length; ix < lx; ix++){
              var size = all_sizes[ix];
              if(tmp.color_objects[clr].sizes.indexOf(size) == -1){
                tmp.color_objects[clr].sizes.push(size);
                tmp.color_objects[clr].size_data[size] = {
                  image: product.product_image_url,
                  price: product.current_price,
                  text: size,
                  value: size
                }
              }
            }
          }
          /* create payload object */
          console.log('merchant product api ' + matching_object.product_api_merchant)
          var merchant_node = matching_object.product_api_merchant.toString();
          var product_node = product_id.toString();
          payload.sites[merchant_node] = {}
          payload.sites[merchant_node].add_to_cart = {}
          payload.sites[merchant_node].add_to_cart[product_node] = {};
          payload.sites[merchant_node].add_to_cart[product_node].title = matching_object.product_name;
          payload.sites[merchant_node].add_to_cart[product_node].brand = matching_object.brand;
          payload.sites[merchant_node].add_to_cart[product_node].price = matching_object.current_price;
          payload.sites[merchant_node].add_to_cart[product_node].original_price = matching_object.retail_price;
          payload.sites[merchant_node].add_to_cart[product_node].image = matching_object.product_image_url;
          payload.sites[merchant_node].add_to_cart[product_node].description = matching_object.long_product_description;
          payload.sites[merchant_node].add_to_cart[product_node].required_field_names = ["color", "size", "quantity"];
          payload.sites[merchant_node].add_to_cart[product_node].required_field_values = {};
          payload.sites[merchant_node].add_to_cart[product_node].required_field_values.color = [];
          payload.sites[merchant_node].add_to_cart[product_node].url = matching_object.product_url;
          payload.sites[merchant_node].add_to_cart[product_node].status = "done";
          payload.sites[merchant_node].add_to_cart[product_node].original_url = matching_object.raw_product_url;
          /* create the colors array objects */
          for(var i = 0, l = tmp.color_names.length; i<l; i++){
            var color = tmp.color_names[i];
            var obj = {
              dep: { size: [] },
              price: matching_object.current_price,
              text: color,
              value: color
            }
            for(var ix = 0, il = tmp.color_objects[color].sizes.length; ix<il; ix++){
              var size_name = tmp.color_objects[color].sizes[ix];
              var size = tmp.color_objects[color].size_data[size_name];
              size.dep = {}
              obj.dep.size.push(size);
            }
            payload.sites[merchant_node].add_to_cart[product_node].required_field_values.color.push(obj);
          }
          $.ajax({
            contentType: 'application/x-www-form-urlencoded',
            crossDomain: true,
            data: $.param({look_product_id: look_item_id, product: payload}),
            type: 'POST',
            url: 'https://ecommerce-service-stage.allume.co/wp-json/products/create_or_update_product_from_affiliate_feeds_and_link_to_look/',
            xhrFields: {
              withCredentials: true
            }
          });
        }
      },
      type: "GET",
      url: '/product_api/get_product/' + product_id  + '/',
    });
  },
  /**
  * @description add an image from the rack to the canvas
  * @param {integer} product_id - id of the product being added
  * @param {string} src - source of the image to be added
  */
  addCanvasImage: function(product_id, src){
    var look_product_obj = {
      layout_position: 1,
      look: $('input#look-id').val(),
      product: product_id,
      cropped_dimensions: null,
      in_collage: 'True',
      cropped_image_code: null       
    }
    $.ajax({
      contentType : 'application/json',
      data: JSON.stringify(look_product_obj),
      success:function(response){
        var img = new Image(); 
        img.src = look_proxy + '' + src;
        img.onload = function() {
          var scale = 1;
          if(this.naturalHeight > 395){
            scale = 395 / this.naturalHeight 
          }
          var fImg = new fabric.Cropzoomimage(this, {
            originX: 'center',
            originY: 'center',
            left: collage.canvas.getWidth()/2,
            top: collage.canvas.getHeight()/2,
            scaleX: scale,
            scaleY: scale,
            prod_id: response.id
          });
          fImg.originalImgSrc = look_proxy + '' + src;
          collage.canvas.add(fImg);
          collage.canvas.setActiveObject(fImg);
          collage.canvas.discardActiveObject();
          $('#adding-product').remove();
          collage.product_cache.push(response);
          collage.setWatermark();
        };
        collage.addAllumeProduct(response.product, response.id);
      },
      type: 'PUT',
      url: '/shopping_tool_api/look_item/0/'
    });
  },
  /**
  * @description object to be used to hold reference to canvas object being created for editing look collages
  */
  canvas: null,
  /**
  * @description field to hold reference to canvas sortable object
  */  
  collageSortable: null,
  /**
  * @description crop and load new image to cropper
  */
  cropImage: function(link){
    var rectangle = collage.cropper.getActiveObject();
    rectangle.visible = false
    var new_image = collage.cropper.toDataURL({
      format: 'jpeg',
      quality: 1,
      left: rectangle.aCoords.tl.x,
      top: rectangle.aCoords.tl.y,
      width: rectangle.width * rectangle.scaleX,
      height: rectangle.height * rectangle.scaleY
    });
    collage.saveCrop(link, new_image);  
  },
  /**
  * @description field to hold reference to cropper canvas object
  */   
  cropper: null,
  /**
  * @description flip active canvas object horizontally
  */
  flipX: function(){
    var activeObject = collage.canvas.getActiveObject();
    if (activeObject) {
      if(activeObject.flipX == true){
        activeObject.flipX = false;
      }else{
        activeObject.flipX = true;
      }
      collage.canvas.renderAll();
    }
  },
  /**
  * @description init function to draw the canvas and add initial look products
  * @param {array} products - array of look products
  */
	init: function(products){
    collage.canvas = new fabric.Canvas('c');
    collage.product_cache = products;
    collage.initial_load = products.length - 1;
    /* add in the watermark */
    var img = new Image(); 
    /* watermark path */
    img.src = '/static/shopping_tool/image/allume_watermark.png';
    img.onload = function() {
      /* scale: 0.1, left: 690, and top: 400 based upon 1365 x 284 watermark dimensions */
      var scale = 0.1;
      var fImg = new fabric.Cropzoomimage(this, {
        originX: 'center',
        originY: 'center',
        left: 690,
        top: 400,
        scaleX: scale,
        scaleY: scale,
        prod_id: 'watermark'
      });
      collage.canvas.add(fImg);
      fImg.selectable = false;
    }
    if(collage.initial_load > -1){
      collage.loadImg()
    }
  },
  /**
  * @description object to be used to keep track of initial count of images
  */  
  initial_load: null,
  /**
  * @description helper function to load/add image to canvas in order to preserve scope
  */
  loadImg:function(){
    var prod = collage.product_cache[collage.initial_load]
    /* if product in collage add to collage other wise add to additional items */
    if(prod.in_collage == true){
      var img = new Image();
      if(prod.cropped_image_code != null){
        img.src = prod.cropped_image_code
      }else{
        img.src = look_proxy + '' + prod.product.product_image_url;
      }
      img.onload = function() {
        var scale = 1;
        if(this.naturalHeight > 395){
          scale = 395 / this.naturalHeight 
        }
        var dims = {
          originX: 'center',
          originY: 'center',
          left: collage.canvas.getWidth()/2,
          top: collage.canvas.getHeight()/2,
          scaleX: scale,
          scaleY: scale,
          prod_id: prod.id
        };
        if(prod.cropped_dimensions != null){
          dims = $.extend(true, {}, JSON.parse(prod.cropped_dimensions));
          dims.originX = 'center';
          dims.originY = 'center';
          dims.prod_id = prod.id;
        }
        var fImg = new fabric.Cropzoomimage(this, dims);
        fImg.originalImgSrc = look_proxy + '' + prod.product.product_image_url;
        collage.canvas.add(fImg);
        /* keep track of loaded object count lood next product if some still remain */
        collage.initial_load--;
        if(collage.initial_load > -1){
          collage.loadImg();
        }else{
          collage.setWatermark();
          collage.canvas.renderAll();
        }
      };
    }else{
      $('#non-collage-items').append(
        '<div class="item"><img class="handle" src="' + prod.product.product_image_url + 
        '"/><a href="#" class="remove" data-lookitemid="' + prod.id +
        '"><i class="fa fa-times"></i></a></div>'
      );
      /* keep track of loaded object count lood next product if some still remain */
      collage.initial_load--;
      if(collage.initial_load > -1){
        collage.loadImg();
      }else{
        collage.setWatermark();
        collage.canvas.renderAll();
      }
    }
  },
  /**
  * @description cache of look products to be used for removal of objects and positioning
  */  
  product_cache: null,
  /**
  * @description save cropped image function
  * @param {DOM Object} link - save link
  * @param {string} new_image - base 64 encoded image data 
  */
  saveCrop: function(link, new_image){
    /* get the link data for the product id */
    var data = link.data();
    var collage_objects = collage.canvas.toObject().objects;
    var correct_canvas_obj, correct_canvas_idx, cache_obj;
    /* find and update the collage object with the new image data */
    for(var i = 0, l = collage_objects.length; i<l; i++){
      if(collage_objects[i].prod_id == data.prodid){
        correct_canvas_obj = collage_objects[i];
        correct_canvas_idx = i;
        break;
      }
    }
    for(var i = 0, l = collage.product_cache.length; i<l; i++){
      if(collage.product_cache[i].id === data.prodid){
        cache_obj = collage.product_cache[i];
        break;
      }
    }
    cache_obj.cropped_image_code = new_image;
    /* update the look product database */
    $.ajax({
      contentType : 'application/json',
      data: JSON.stringify({cropped_image_code: new_image}),
      success:function(response){},
      type: 'PUT',
      url: '/shopping_tool_api/update_cropped_image_code/' + cache_obj.id + '/'
    });
    /* fade out the various cropper overlays */
    $('#crop-look-image').fadeOut();
    $('#pg-crop-look-image').fadeOut();
    collage.canvas.remove(collage.canvas.item(correct_canvas_idx));
    /* add the new image to the collage */
    var img = new Image(); 
    img.src = new_image;
    img.onload = function() {
      var scale = 1;
      if(this.naturalHeight > 395){
        scale = 395 / this.naturalHeight 
      }
      var fImg = new fabric.Cropzoomimage(this, {
        originX: 'center',
        originY: 'center',
        left: collage.canvas.getWidth()/2,
        top: collage.canvas.getHeight()/2,
        scaleX: scale,
        scaleY: scale,
        prod_id: data.prodid
      });
      fImg.originalImgSrc = link.siblings('a.restart').data('path');
      collage.canvas.add(fImg);
    };
  },
  /**
  * @description set the current active object to bottom of layer stack 
  */  
  sendBack: function(){
    var activeObject = collage.canvas.getActiveObject();
    if (activeObject) {
      collage.canvas.sendToBack(activeObject);
    }
  },
  /**
  * @description set the current active object to top of layer stack 
  */
  sendForward: function(){
    var activeObject = collage.canvas.getActiveObject();
    if (activeObject) {
      collage.canvas.bringToFront(activeObject);
      collage.setWatermark();
    }
  },
  /**
  * @description initial set up of the crop image overlay
  */
  setUpCrop: function(){
    var activeObject = collage.canvas.getActiveObject();
    if (activeObject) {
      /* add the new canvas and initialize with fabric */
      $('#cropper-container').html('<canvas id="crop-canvas" width="415" height="415"></canvas>');
      collage.cropper = new fabric.Canvas('crop-canvas');
      /* add the image to be cropped to the cropper canvas */
      collage.setUpCropperImage(activeObject.orgSrc, activeObject.prod_id, 'initial');
      /* set initial states of cropper buttons */
      $('#cropper-btns').find('a.restart').data('path', activeObject.originalImgSrc).data('prodid', activeObject.prod_id)
      .end().find('a.crop').data('prodid', activeObject.prod_id);
    }    
  },
  /**
  * @description creates the initial cropper rect
  */
  setUpCropper: function() { 
    var obj = collage.cropper.getActiveObject(); 
    var el = new fabric.Rect({
      fill: 'transparent',
      originX: 'center',
      originY: 'center',
      stroke: '#555',
      strokeDashArray: [7, 7],
      opacity: 1,
      width: 1,
      height: 1,
      cornerColor: '#333',
      borderColor: 'transparent',
      hasRotatingPoint:false,
      objectCaching: false
    });
    el.left = collage.cropper.getWidth()/2 + 1;
    el.top = collage.cropper.getHeight()/2 + 1;
    el.width = (obj.width * obj.scaleX) - 2;
    el.height = (obj.height * obj.scaleY) - 2;
    collage.cropper.add(el);
    collage.cropper.setActiveObject(el);
    obj.selectable = false
  },
  /**
  * description helper function to set up cropper image 
  * @param {string} src - image src
  * @param {integer} prod_id - product id
  * @param {string} time - string identifier to trigger certain UI/UX condiontal changes
  */
  setUpCropperImage: function(src, prod_id, time){
    var img = new Image();
    img.src = src;
    img.onload = function() {
      var scale = 1;
      if(this.naturalHeight > 395){
        scale = 395 / this.naturalHeight 
      }
      var dims = {
        originX: 'center',
        originY: 'center',
        left: collage.cropper.getWidth()/2,
        top: collage.cropper.getHeight()/2,
        scaleX: scale,
        scaleY: scale,
        prod_id: prod_id
      }
      var fImg = new fabric.Cropzoomimage(this, dims);
      collage.cropper.add(fImg);
      collage.cropper.setActiveObject(fImg);
      collage.setUpCropper();
      if(time == 'initial'){
        $('#crop-look-image').fadeIn();
        $('#adding-product').remove();
      }
    };
  },
  /**
  * @description extend fabric with our new object class name 
  * include several methods for our Cropzoomimage class which will be used for
  * saving and manipulating the canvas object
  */
  setUpObject: function(){
    fabric.Cropzoomimage = fabric.util.createClass(fabric.Image, {
      type: 'cropzoomimage',
      zoomedXY: false,
      initialize: function(element, options){
        options || (options = {});
        this.callSuper('initialize', element, options);
        this.set({
          orgSrc: element.src,
          cx: 0, 
          cy: 0,
          cw: element.width, 
          ch: element.height,
          zoomX: 0,
          zoomY: 0,
          zoomZ: 0
        });
        this.setControlsVisibility({
          mt: false, 
          mb: false, 
          ml: false, 
          mr: false,
          mtr: false
        });
      },
      zoomBy: function(x, y, z, callback) {
        this.zoomX += x;
        this.zoomY += y;
        this.zoomZ += z;
        if (x || y) { this.zoomedXY = true; }
        this.cx += x;
        this.cy += y;

        if (z) {
          this.cw -= z;
          this.ch -= z/(this.width/this.height);
        }

        if (z && !this.zoomedXY) { 
          this.cx = this.width / 2 - (this.cw / 2);
          this.cy = this.height / 2 - (this.ch / 2);
        }

        if (this.cw > this.width) { this.cw = this.width; }
        if (this.ch > this.height) { this.ch = this.height; }
        if (this.cw < 1) { this.cw = 1; }
        if (this.ch < 1) { this.ch = 1; }
        if (this.cx < 0) { this.cx = 0; }
        if (this.cy < 0) { this.cy = 0; }
        if (this.cx > this.width - this.cw) { this.cx = this.width - this.cw; }
        if (this.cy > this.height - this.ch) { this.cy = this.height - this.ch; }

        this.rerender(callback);
      },
      rerender: function(callback){
        var img = new Image(), obj = this;
        img.onload = function() {
          var canvas = fabric.util.createCanvasElement();
          canvas.width = obj.width;
          canvas.height = obj.height;
          canvas.getContext('2d').drawImage(this, obj.cx, obj.cy, obj.cw, obj.ch, 0, 0, obj.width, obj.height);
          img.onload = function() {
            obj.setElement(this);
            obj.set({
              left: obj.left,
              top: obj.top,
              angle: obj.angle
            });
            obj.setCoords();
            if (callback) { callback(obj); }
          };
          img.src = canvas.toDataURL('image/png');
        };
        img.src = this.orgSrc;
      },
      toObject: function(){
        return fabric.util.object.extend(this.callSuper('toObject'), {
          orgSrc: this.orgSrc,
          cx: this.cx,
          cy: this.cy,
          cw: this.cw,
          ch: this.ch,
          prod_id: this.prod_id,
          zoomX: this.zoomX,
          zoomY: this.zoomY,
          zoomZ: this.zoomZ,
          zoomedXY: this.zoomedXY,
          originalImgSrc: this.originalImgSrc
        });
      }
    });
    fabric.Cropzoomimage.async = true;
    fabric.Cropzoomimage.fromObject = function(object, callback) {
      fabric.util.loadImage(object.src, function(img) {
        fabric.Image.prototype._initFilters.call(object, object, function(filters) {
          object.filters = null;
          var instance = new fabric.Cropzoomimage(img, object);
          if (callback) { callback(instance); }
        });
      }, null, object.crossOrigin);
    };
  },
  /**
  * @description set up the polygon cropper overlay
  */
  setUpPolygonCrop: function(){
    var activeObject = collage.canvas.getActiveObject();
    if (activeObject) {
      /* add the new canvas and initialize with fabric */
      $('#pg-cropper-container').html('<canvas id="pg-cropper" width="415" height="415"></canvas>');
      $('#pg-crop-look-image').fadeIn();
      collage.setUpPolygonCropper(activeObject.orgSrc, activeObject.prod_id);
      $('#pg-cropper-btns').find('a.restart').data('path', activeObject.originalImgSrc).end()
      .find('a.save').data('prodid', activeObject.prod_id);
    }
  },
  /**
  * @description set up the polygon cropper canvas object and functionality
  * @param {string} src - the path or data of image to be cropped
  */
  setUpPolygonCropper: function(src){
    var canvas = document.getElementById("pg-cropper");
    var ctx = canvas.getContext("2d");
    ctx.strokeStyle = 'black';
    ctx.imageSmoothingEnabled = false;    
    var cw = canvas.width 
    var ch = canvas.height 
    var $canvas = $("#pg-cropper");
    var canvasOffset = $canvas.offset();
    var offsetX = canvasOffset.left;
    var offsetY = canvasOffset.top;
    var img_scale = 1
    /* an array to hold user's click-points that define the clipping area */
    var points = [];
    /* load the image */
    var img = new Image();
    img.src = src;
    img.onload = function(){
      if(this.naturalHeight > 415){
        img_scale = 415 / this.naturalHeight 
      }else if(this.naturalWidth > 415){
        img_scale = 415 / this.naturalWidth 
      }
      /* draw the image to the canvas */
      drawImage();
      /* listen for mousedown */
      $('#pg-cropper').mousedown(function(e){ handleMouseDown(e); });
    }
    /*
    * @description private function to add the image to the canvas 
    */
    function drawImage(){
      ctx.clearRect(0, 0, cw, ch);
      var img_width = img.naturalWidth * img_scale;
      var img_height = img.naturalHeight * img_scale;
      var start_x = 0;
      var start_y = 0;
      if(img_width < 415){ start_x = (415 - img_width) / 2 }
      if(img_height < 415){ start_y = (415 - img_height) / 2 }
      ctx.drawImage(img, start_x, start_y, img_width, img_height);
    }
    /**
    * @description private function to draw the point by point polygon outline 
    */
    function outlineIt(){
      drawImage();
      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);
      for(var i = 0, l = points.length; i<l; i++){
        ctx.lineTo(points[i].x, points[i].y);
      }
      ctx.closePath();
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(points[0].x, points[0].y, 5, 0, Math.PI*2);
      ctx.closePath();
      ctx.stroke();
    }
    /**
    * @descritpion private function allowing for mousedown tracking to build the polygon 
    */
    function handleMouseDown(e){
      e.preventDefault();
      e.stopPropagation();
      /* calculate the xy relative to browser window */
      var mx =parseInt(e.clientX - offsetX);
      var my =parseInt(e.clientY - offsetY);
      /* push the clicked point to the points array */
      points.push({ x: mx, y: my });
      /* show the user an outline of their current clipping path */
      outlineIt();
      /* if the user clicked back in the original circle then complete the clip */
      if( points.length > 1) {
        var dx = mx - points[0].x;
        var dy = my - points[0].y;
        if(dx * dx + dy * dy < 10*10){
          clipIt();
        }
      }
    }
    /**
    * @description private function to clip the image and display to user 
    */
    function clipIt(){
      /* calculate the size of the user's clipping area */
      var minX = 10000;
      var minY = 10000;
      var maxX = -10000;
      var maxY = -10000;
      for(var i = 1, l = points.length; i<l; i++){
        var p = points[i];
        if( p.x < minX ){ minX = p.x; }
        if( p.y < minY ){ minY = p.y; }
        if( p.x > maxX ){ maxX = p.x; }
        if( p.y > maxY ){ maxY = p.y; }
      }
      var width = maxX - minX;
      var height = maxY - minY;
      /* clip the image into the user's clipping area */
      ctx.save();
      ctx.clearRect(0,0,cw,ch);
      ctx.beginPath();
      ctx.moveTo(points[0].x,points[0].y);
      for(var i=1;i<points.length;i++){
        var p=points[i];
        ctx.lineTo(points[i].x,points[i].y);
      }
      ctx.closePath();
      ctx.clip();
      var img_width = img.naturalWidth * img_scale;
      var img_height = img.naturalHeight * img_scale;
      var start_x = 0;
      var start_y = 0;
      if(img_width < 415){ start_x = (415 - img_width) / 2 }
      if(img_height < 415){ start_y = (415 - img_height) / 2 }
      ctx.drawImage(img, start_x, start_y, img_width, img_height);
      ctx.restore();
      /* create a new canvas to get the image data */
      $('body').append('<canvas id="tmp-crop"></canvas>')
      var c = document.getElementById("tmp-crop");
      var cx = c.getContext('2d');
      /* resize the new canvas to the size of the clipping area */
      c.width = width;
      c.height = height;
      /* set the background to white */
      cx.fillStyle = "#ffffff";
      cx.fillRect(0, 0, c.width, c.height);
      /* draw the clipped image from the main canvas to the new canvas */
      cx.drawImage(canvas, minX, minY, width, height, 0, 0, width, height);
      /* get the image data */
      var pg_crop = c.toDataURL('image/jpeg', 1.0);
      $('#pg-cropper-btns a.save').data('path', pg_crop);
      /* clear previous clip points */ 
      points.length = 0;
      /* remove the tmp crop canvas */
      $('#tmp-crop').remove();
    }
  },
  /**
  * @description funtion to place the watermark object on top of the stack
  */ 
  setWatermark: function(){
    var cv_objs = collage.canvas.toObject();
    for(var i = 0, l = cv_objs.objects.length; i<l; i++){
      var prod = cv_objs.objects[i];
      if(prod.prod_id == 'watermark'){
        collage.canvas.bringToFront(collage.canvas.item(i));
        break;
      }
    }
  },
  /**
  * @description removal of object from canvas and from look products
  */
  trash: function(){
    var activeObject = collage.canvas.getActiveObject();
    if (activeObject) {
      var idx = null;
      for(var i = 0, l = collage.product_cache.length; i<l; i++){
        if(collage.product_cache[i].id === activeObject.prod_id){
          idx = i;
          break;
        }
      }
      if(idx != null){
        $.ajax({
          success:function(response){},
          type: 'DELETE',
          url: '/shopping_tool_api/look_item/' + collage.product_cache[idx].id + '/'
        });        
        collage.product_cache.splice(idx,i);
      }
      collage.canvas.remove(activeObject);
    }
  },
  /**
  * @description update collage and save look
  * @param {DOM Object} div - div in comp looks that is the look being edited
  */
  updateCollage: function(div){
    /* set ui to show that we are updating a look */
    div.addClass('updating').removeClass('editing').find('div.editing').html('loading changes...');
    /* discard the active object so stack is correctly rendered */
    collage.canvas.discardActiveObject();
    /* get canvas object so that we can update look products */
    var changes = collage.canvas.toObject();
    /* update the look */
    look_builder.updateLook(div, $('input#look-id').val(), $('#look-name').val(), $('#look-desc').val());
    /* cahce the look id so we have it for the update calls for look products */
    var look_id = $('input#look-id').val();
    /* loop through canvas objects and correlate them to look products */
    for(var i = 0, l = changes.objects.length; i<l; i++){
      /* get the image */
      var prod = changes.objects[i];
      if(prod.prod_id != 'watermark'){
        var product_id = null;
        var crop_src = null;
        for(var ix = 0, lx = collage.product_cache.length; ix<lx; ix++){
          var record = collage.product_cache[ix];
          if(record.id == prod.prod_id){
            if(typeof record.product == 'object'){
              product_id = record.product.id;
            }else{
              product_id = record.product;
            }
            if(record.cropped_image_code != undefined){
              crop_src = record.cropped_image_code;
            }
            break;
          }
        }
        /* set the dimensions to be saved */
        var dims = {
          angel: prod.angle,
          left: prod.left,
          top: prod.top,
          scaleX: prod.scaleX,
          scaleY: prod.scaleY,
          skewX: prod.skewX,
          skewY: prod.skewY,
          cx: prod.cx,
          cy: prod.cy,
          cw: prod.cw,
          ch: prod.ch,
          flipX: prod.flipX,
          width: prod.width,
          height: prod.height,
          zoomX: prod.zoomX,
          zoomY: prod.zoomY,
          zoomZ: prod.zoomZ,
          zoomedXY: prod.zoomedXY,
          originalImgSrc: prod.originalImgSrc
        }
        /* set the look_product object */
        var look_product_obj = {
          layout_position: i,
          look: look_id,
          product: product_id,
          cropped_dimensions: JSON.stringify(dims),
          in_collage: 'True',
          cropped_image_code: crop_src     
        }
        /* update the look product */
        $.ajax({
          contentType : 'application/json',
          data: JSON.stringify(look_product_obj),
          success:function(response){},
          type: 'PUT',
          url: '/shopping_tool_api/look_item/' + prod.prod_id + '/'
        });
      }
    }
    /* reset the collage cache holders so collage is ready for new look to edit */
    collage.canvas = null;
    collage.initial_load = null;
    collage.product_cache = null;  
  },
  /**
  * @description zoomBy function for image cropping
  * @param {integer} x - value to zoom in x axis
  * @param {integer} y - value to zoom in y axis
  * @param {integer} z - value to zoom in z axis
  */    
  zoomBy: function(x, y, z) {
    var activeObject = collage.canvas.getActiveObject();
    if (activeObject) {
      activeObject.zoomBy(x, y, z, function(){collage.canvas.renderAll()});
    }
  }
}