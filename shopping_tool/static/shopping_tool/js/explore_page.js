/**
* @description explore_page namespace object, conatining the functionality and templates for the explore page
*/
var explore_page = {
  /** 
  * @description cache of styling session
  */
  session_id: '',
  /**
  * @description init function applying the functionality to the page elements
  */
  init: function(){
    rack_builder.init();
    look_builder.functionality();
    /* cache the session id */
    explore_page.session_id = $('body').data('stylesession');
  }  
}