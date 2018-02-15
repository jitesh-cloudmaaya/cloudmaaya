/**
* @description utilities namespace object, conatining the commonly used utility type functions
*/
var utils = {
  /**
  * @description capitalize the first letter of a string
  * @param {string} str - the string to process
  * @returns {string} capitalized first letter of the same string
  */
  capitalizeFirstLetter: function(str){
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  },  
  /**
  * @description capitalize the first letter of every word in a string
  * @param {string} str - the string to process
  * @returns {string} fixed string
  */
  capitalizeEveryWord: function(str){
    return str.replace(/\w\S*/g, function(txt){
      return utils.capitalizeFirstLetter(txt);
    });
  },
  /**
  * @description client details and presentation checks
  */  
  client: function(){
    /* add keyboard shortcuts for client open/close */
    Mousetrap.bind('shift+a+s', function(e) {
      $('#user-card').toggleClass('show')
      return false;
    });    
    var clip = $('#user-clip');
    clip.delay(750)
      .queue(function (next) { 
        $(this).addClass('ready').width($('#user-clip span.name').width()); 
        next(); 
      });
    clip.click(function(e){
      e.preventDefault();
      $('#user-card').toggleClass('show').removeClass('looker');
    });
    $('#design-look-user-toggle').click(function(e){
      e.preventDefault();
      $('#user-card').addClass('show').addClass('looker');
    }).html('View ' + clip.data('username'))
    /* correctly display bra size */
    var bra = $('#bra-size');
    var bra_size = bra.data('sizes');
    if((bra_size != undefined)&&(typeof bra_size == 'object')){
      bra.html('<em>bra:</em>' + bra_size.band + '' + bra_size.cup);
      $('#prev-bra-size').html('<em>bra:</em>' + bra_size.band + '' + bra_size.cup);
    }
    /* correctly display birthday */
    var bd = $('#client-birthday');
    var bday = bd.data('bd');
    if((bday != undefined)&&(typeof bday == 'object')){
      var proc_bday = moment(bday.month +'/' + bday.day +'/' + bday.year, 'M/D/YYYY');
      var now = moment();
      var diff = now.diff(proc_bday, 'years')
      var bd_display = '<em>age:</em>' + diff + ' years old';
      bd.html(bd_display);
      $('#prev-client-birthday').html(bd_display);
    }
    /* check to see if the social links are valid, if not hide, if they are valid up the link index count */
    var social = $('#client-social');
    var social_link_index = 0;
    $.each(social.find('a'), function(idx){
      var link = $(this);
      if(link.attr('href') == 'None'){
        link.hide();
      }else{
        social_link_index++;
      }
    });
    /** correctly display where the client lives */
    var locale = $('#client-locale');
    var city_state = locale.data('cs');
    if((city_state != undefined)&&(typeof city_state == 'object')){
      var cs_display = city_state.city + ', ' + city_state.state;
      locale.html('<em>location:</em>' + cs_display);
      $('#prev-client-locale').html('<em>location:</em>' + cs_display)
      $('#client-weather-locale').html('Seasonal norms for ' + cs_display + ':');
    }    
    /* if link idex is 0, no social links are valid thus hide the whole social div */
    if(social_link_index == 0){ social.hide(); }
    /* client card tabs */
    $('#client-tabs a').click(function(e){
      e.preventDefault();
      var link = $(this);
      var href = link.attr('href')
      var div = $(href);
      /* calculate the correct max height of tab sections */
      var h = 625 - ($('#client-tabs').outerHeight() + $('#user-card div.social').outerHeight() + $('#user-card span.goal').outerHeight());
      div.css('maxHeight', h + 'px')
      if(link.hasClass('on') == false){
        link.addClass('on').siblings('a').removeClass('on');
        div.addClass('show').siblings('div.client-section').removeClass('show'); 
        if(href == '#client-notes'){
          div.closest('div.client-sections').addClass('notes');
        }else{
          div.closest('div.client-sections').removeClass('notes');
        }
      }
    });
    /* add notes form toggle */
    $('#add-note-toggle').click(function(e){
      e.preventDefault();
      $('#add-notes-form').slideToggle();
    });
    /* submit the new note */
    $('#submit-note').click(function(e){
      e.preventDefault();
      var nl = $('#note-list');
      var current_stylist = parseInt($('#stylist').data('stylistid'));
      var note_obj ={
        "stylist": current_stylist,
        "client": parseInt($('#user-clip').data('userid')),
        "styling_session": parseInt($('body').data('stylesession')),
        "notes": $('#added-note').val(),
        "visible": 1
      }
      $('#add-notes-form').slideToggle();
      $.ajax({
        beforeSend: function(xhr){
          nl.prepend(
            '<div id="notes-loader">' +
            '<span class="pulse_loader"></span>' +
            '<span class="pulse_message">adding your note...</span>' +
            '</div>'
          );
        },
        contentType : 'application/json',
        data: JSON.stringify(note_obj),        
        success: function(response){
          $('#notes-loader').remove();
          nl.prepend(utils.noteTemplate(response, current_stylist));
          $('#added-note').val('');
          var header = $('#client-notes h3');
          var count = parseInt(header.data('num')) + 1;
          var header_txt = count == 1 ? '1 Note' : count + ' Notes';
          header.html(header_txt).data('num',count);
        },
        type: 'PUT',
        url:'/shopping_tool_api/styling_session_note/0/'
      });
    });
    /* delete not functionality */
    $('#note-list').on('click', 'a.delete-note', function(e){
      e.preventDefault();
      var link = $(this);
      $('#delete-note-overlay').find('a.yes').data('noteid', link.data('noteid')).end().fadeIn();
    });
    /* delete note confirm dialog */
    $('#delete-note-overlay').find('a.yes').click(function(e){
      e.preventDefault();
      var link = $(this);
      $('#client-note-id-' + link.data('noteid')).remove();
      $.ajax({
        type: 'DELETE',
        url: '/shopping_tool_api/styling_session_note/' + link.data('noteid') + '/'
      });
      $('#delete-note-overlay').fadeOut();
       var header = $('#client-notes h3');
        var count = parseInt(header.data('num')) - 1;
        var header_txt = count == 1 ? '1 Note' : count + ' Notes';
        if(count == 0){
          header_txt = 'There are no notes for this client.'
        }
        header.html(header_txt).data('num',count);
    }).end().find('a.cancel').click(function(e){
      e.preventDefault();
      $('#delete-note-overlay').fadeOut();
    });
    /* load the client notes */
    $.ajax({
      success: function(response){
        var ui_div = $('#note-list');
        var current_stylist = parseInt($('#stylist').data('stylistid'));
        var count = response.length;
        if(count > 0){
          var header_txt = count == 1 ? '1 Note' : count + ' Notes';
          $('#client-notes h3').html(header_txt).data('num', count);
          var notes_markup = [];
          for(var i = 0; i<count; i++){
            var note = response[i];
            notes_markup.push(utils.noteTemplate(note, current_stylist));
          }
          ui_div.html(notes_markup.join(''));
        }else{
          $('#client-notes h3').html('There are no notes for this client.').data('num', count);
        }
      },
      url:'/shopping_tool_api/styling_session_notes/' + $('#user-clip').data('userid') + '/'
    });
    /* quick set of rack ids */
    for(var i = 0, l = initial_rack.length; i<l; i++){
      var obj = initial_rack[i];
      var sku = obj.id + '_' + obj.merchant_id + '_' + obj.product_id + '_' + obj.sku;
      rack_builder.rack_product_ids.push(sku);
    }
  },
  /**
  * @description create function which sets document cookies
  * @param {string} name - name of teh cookie
  * @param {string} value - content to be stored in the cookie
  * @param {integer} days - number of days to keep th ecookie fresh
  */
  createCookie: function(name, value, days) {
    var expires;
    if (days) {
      var date = new Date();
      date.setTime(date.getTime() + (days*24*60*60*1000));
      expires = "; expires=" + date.toGMTString();
    } else {
      expires = "";
    }
    document.cookie = name + "=" + value + expires + "; path=/";
  },  
  /**
  * @description make a groups of DOM objects all the same height
  * @params {DOM Array} - array of DOM objects
  */
  equalHeight: function(group) {
    var tallest = 0;
    group.each(function() {
      var thisHeight = $(this).height();
      if(thisHeight > tallest) {
        tallest = thisHeight;
      }
    });
    group.height(tallest);
  },
  /**
  * @description helper function to set cookie to no value
  * @param {string} name - name of cookie to erase
  */
  eraseCookie: function(name) {
    utils.createCookie(name, "", -1);
  },  
  /**
  * @description menu button functionality
  */
  menu: function(){
    $('#menu-toggle').click(function(e){
      e.preventDefault();
      $('#nav-menu').fadeIn();
      $('#nav-menu div.menu').addClass('show');
    });
    $('#close-nav-menu').click(function(e){
      e.preventDefault();
      $('#nav-menu div.menu').removeClass('show');
      $('#nav-menu').fadeOut();
    });
  },
  /**
  * @description template for note display
  * @params {object} note - json for note object
  * @params {integer} stylist_id - id of the current stylist logged in
  * @returns {string} HTML
  */
  noteTemplate: function(note, stylist_id){
    var delete_link = '';
    if(note.stylist == stylist_id){
      delete_link = '<a href="#" data-noteid="' + note.id + '" class="delete-note"><i class="fa fa-times"></i></a>'
    }
    return '<div class="client-note" id="client-note-id-' + note.id + '"><p>' + note.notes+ '</p>' +
      '<span class="date">' + moment(note.last_modified).format('MMMM Do, YYYY h:mm a') + 
      '</span><span class="tail"></span><span class="name">' + note.stylist.first_name + 
      ' ' + note.stylist.last_name + '</span>' + delete_link + '</div>';
  },
  /**
  * @description processing and template for pagination of results
  * @param {integer} page - page currently displayed
  * @param {integer} total - total number of items in result set
  * @param {integer} per_page - number of items per page payload
  */  
  pagerTemplate: function(page, total, per_page){
    var markup = [];
    var total_pages = Math.floor(total / per_page);
    var excess = total % per_page;
    if(excess > 0){ total_pages++};
    /* create pager message string */
    var showing_low = numeral(((page * per_page) - per_page + 1)).format('0,0');
    var showing_high = numeral(page * per_page).format('0,0');
    if((page * per_page) > total){
      showing_high = numeral(total).format('0,0');
    }
    var result_total = numeral(total).format('0,0');
    $('#pager-message').html(
      'Showing <strong>' + showing_low + '</strong> - <strong>' + 
      showing_high + '</strong> of <strong>' + result_total + '</strong>'
    );
    /**
    * @description private function to gerenate links
    * @param {integer} page - current page
    * @param {integer} low - low number to use in loop
    * @param {integer} high - high number to use in loop
    * @returns {string} HTML
    */        
    function makePager(page, low, high){
      var pager = [];
      for(var i = (page - low); i < (page + high); i++){
        if(i > 0){        
          if(i == page){
            pager.push('<span class="current">' + i + '</span>');
          }else{
            if(i <= total_pages){
              pager.push('<a href="#" data-page="' + i + '" class="page">' + i + '</a>');
            }
          }
        }
      }
      return pager.join('');
    }
    if(page > 1){
      markup.push(
        '<a href="#" data-page="' + (page - 1) + 
        '" class="page prev"><i class="fa fa-angle-left"></i>Previous</a>'
      );
    }
    if(total_pages > page){
      markup.push(
        '<a href="#" data-page="' + (page + 1) + 
        '" class="page next">Next<i class="fa fa-angle-right"></i></a>'
      );
    }
    if((page > 3)&&(page <= (total_pages - 3))){
      markup.push(
        '<a href="#" data-page="1" class="page">1</a>' +
        '<span class="break">...</span>' +
        makePager(page, 1, 2)
      );
      if((page + 2) < total_pages){
        markup.push(
          '<span class="break">...</span>' +
          '<a href="#" data-page="' + total_pages + '" class="page">' + total_pages + '</a>'
        )          
      }
    }else{
      var show_max_ellipse = false;
      if(page == 1){
        var max = total_pages > 5 ? 4 : 5;
        markup.push(
          makePager(page, 2, max)
        );
        if((page + max) < total_pages){ show_max_ellipse = true }
      }else if(page == 2){
        var max = total_pages > 5 ? 3 : 4;
        markup.push(
          makePager(page, 1, max)
        );  
        if((page + max) < total_pages){ show_max_ellipse = true }              
      }else if(page == 3){
        var max = total_pages > 5 ? 2 : 3;
        markup.push(
          makePager(page, 2, max)
        );
        if((page + max) < total_pages){ show_max_ellipse = true } 
      }else if(page == total_pages){
        var min = 2; 
        if(total_pages > 5){ min = 3 }else if(total_pages <= 5){ min = 4}; 
        if((page - min) > 2 ){
          markup.push(
            '<a href="#" data-page="1" class="page">1</a>' +
            '<span class="break">...</span>'
          );
        } 
        markup.push(
          makePager(page, min , 2)
        );       
      }else if(page == (total_pages - 1)){
        var min = 3; 
        if(total_pages > 5){ min = 2 }else if(total_pages <= 5){ min = 3}; 
        if((page - min) > 2 ){
          markup.push(
            '<a href="#" data-page="1" class="page">1</a>' +
            '<span class="break">...</span>'
          );
        } 
        markup.push(
          makePager(page, min , 2)
        );       
      }else if(page == (total_pages - 2)){
        var min = 4; 
        if(total_pages > 5){ min = 1 }else if(total_pages <= 5){ min = 2}; 
        if((page - min) > 2 ){
          markup.push(
            '<a href="#" data-page="1" class="page">1</a>' +
            '<span class="break">...</span>'
          );
        } 
        markup.push(
          makePager(page, min , 3)
        );       
      }
      if(show_max_ellipse == true){
        markup.push(
          '<span class="break">...</span>' +
          '<a href="#" data-page="' + total_pages + '" class="page">' + total_pages + '</a>'
        );
      }
    }
    $('#pager').html(markup.join(''));
  },
  /**
  * @description parses a query string into a json object
  * @param {string} queryString - the query string
  * @returns {object} - key/value pairs of param/value(s) as JSON
  */
  parseQuery: function(queryString) {
    var query = {};
    var pairs = (queryString[0] === '?' ? queryString.substr(1) : queryString).split('&');
    for (var i = 0; i < pairs.length; i++) {
      var pair = pairs[i].split('=');
      query[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
    }
    return query;
  },
  /**
  * @description read the value of a give cookie name
  * @param {string} name - the name of the cookie
  * @returns {string|null}
  */
  readCookie: function(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
      var c = ca[i];
      while (c.charAt(0) === ' ') {
        c = c.substring(1,c.length);
      }
      if (c.indexOf(nameEQ) === 0) {
        return c.substring(nameEQ.length,c.length);
      }
    }
    return null;
  },
  /**
  * @description read url params value from window.location.search
  * @param {string} param - parameter we are checking for
  * @returns {string | null} returns param value or null if not present
  */
  readURLParams: function(param){
    var match = RegExp('[?&]' + param + '=([^&]*)').exec(window.location.search);
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
  }
}