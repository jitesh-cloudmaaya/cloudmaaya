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
  }
}