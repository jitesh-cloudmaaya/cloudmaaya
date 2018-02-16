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
                  image: product.raw_product_url,
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
      cropped_dimensions: null        
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
          //fImg.setCrossOrigin('anonymous');
          collage.canvas.add(fImg);
          collage.canvas.setActiveObject(fImg);
          $('#adding-product').remove();
          collage.product_cache.push(response);
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
  * @description init function to draw the canvas and add initial look products
  * @param {array} products - array of look products
  */
	init: function(products){
    collage.canvas = new fabric.Canvas('c');
    collage.product_cache = products;
    collage.initial_load = products.length - 1;
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
    var img = new Image();
    img.src = look_proxy + '' + prod.product.product_image_url;
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
      collage.canvas.add(fImg);
      collage.canvas.setActiveObject(fImg);
      /* if picture was zoomed call the zoom function and correctly display zoomed object */
      if(dims.zoomedXY){
        collage.zoomBy(dims.zoomX, dims.zoomY, dims.zoomZ);
      }
      /* keep track of loaded object count lood next image if some still remain */
      collage.initial_load--;
      if(collage.initial_load > -1){
        collage.loadImg();
      }
    };
  },
  /**
  * @description cache of look products to be used for removal of objects and positioning
  */  
  product_cache: null,
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
    }
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
          zoomedXY: this.zoomedXY
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
    look_builder.updateLook(true, div);
    /* cahce the look id so we have it for the update calls for look products */
    var look_id = $('input#look-id').val();
    /* loop through canvas objects and correlate them to look products */
    for(var i = 0, l = changes.objects.length; i<l; i++){
      /* get the image */
      var prod = changes.objects[i];
      var product_id = null;
      for(var ix = 0, lx = collage.product_cache.length; ix<lx; ix++){
        var record = collage.product_cache[ix];
        if(record.id == prod.prod_id){
          if(typeof record.product == 'object'){
            product_id = record.product.id;
          }else{
            product_id = record.product;
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
        width: prod.width,
        height: prod.height,
        zoomX: prod.zoomX,
        zoomY: prod.zoomY,
        zoomZ: prod.zoomZ,
        zoomedXY: prod.zoomedXY
      }
      /* set the look_product object */
      var look_product_obj = {
        layout_position: i,
        look: look_id,
        product: product_id,
        cropped_dimensions: JSON.stringify(dims)       
      }
      /* update the look product */
      $.ajax({
        contentType : 'application/json',
        data: JSON.stringify(look_product_obj),
        success:function(response){
          
        },
        type: 'PUT',
        url: '/shopping_tool_api/look_item/' + prod.prod_id + '/'
      });
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