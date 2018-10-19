// This file is the major javascript for the final sale check
// function loadData(){
//     $.ajax({
//         contentType : 'application/json',
//         data: JSON.stringify({
//             "allume_cart_id": '',
//             "description": '',
//             "allume_styling_session": look_builder.session_id,
//             "stylist": look_builder.stylist_id,
//             "collage": null     
//         }),
//         error: function(response){
//             console.log('error');
//         },
//         success:function(response){
//             console.log('done');
//         }
//     })
// }


function loadData(data){
    data = JSON.parse(data)
}