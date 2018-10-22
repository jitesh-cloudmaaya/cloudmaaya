// This file is the major javascript for the final sale check

result = {};
result['items'] = {}
current_item = 1;

// example format
// data = '{
// "1": {"item_id":345, "url":"https://www.7forallmankind.com/cold-shoulder-tie-top-in-soft-white.html?cid=linkshareaff", "detail":"Black, Large"}, 
// "2": {"item_id":361, "url":"https://www.allume.co", "detail":"Yellow"}, 
// "number_of_items":2,
// "allume_cart_id": 32435
// }';

function loadData(cart_id){

    allume_cart_id = cart_id
    result['allume_cart_id'] = allume_cart_id

    $.ajax({
        contentType : 'application/json',
        data: {"allume_cart_id": allume_cart_id},
        error: function(response){
            alert('failed to load data for this cart');
        },
        success:function(response){
            data = response;
            number_of_item = data['number_of_items']
            if (number_of_item>0) {
                showProduct(data[current_item]);
            }
            else{
                $("body").html(' <h3> this cart has nothing to check, <br> please close this window </h3>')
            }
        },
        type: 'GET',
        url: '/order_management/get_unchecked_final_sale_data/'
      })
}

// approve
function approveItem(){
    item_id = data[current_item]['item_id']
    result['items'][item_id] = {}
    result['items'][item_id]['final_sale'] = false
    result['items'][item_id]['order_id'] = data[current_item]['order_id']
    nextItem()
}

// mark final sale
function markFinalSale(){
    item_id = data[current_item]['item_id']
    result['items'][item_id] = {}
    result['items'][item_id]['final_sale'] = true
    result['items'][item_id]['order_id'] = data[current_item]['order_id']
    nextItem()
}

// next item
function nextItem(){
    if (current_item < number_of_item){
        current_item += 1;
        showProduct(data[current_item])
    }
    else
    {
        var flag = checkIfFinish();
        if (flag == true){
            finishRedirect();
        }
        else{
            alert('there are still items in the previous page have not been checked yet');
        }
    }
}

// previous item
function previousItem(){
    if (current_item > 1){
        current_item -= 1;
        showProduct(data[current_item]);
    }
    else{
        alert('first item already');
    }
}

// show a product
function showProduct(productDict){
    $("#frame").prop('src', '/order_management/proxy?url=' + encodeURIComponent(productDict['url']));
    $("#detail").text(productDict['detail']);
    $("#product_page").attr('href', productDict['url'])
    // show status
    if (productDict['item_id'] in result){
        if (result[productDict['item_id']]['final_sale']){
            $("#status").html('<h5 style="color:green"><i class="fas fa-check-circle"></i>Good</h5>');
        }
        else{
            $("#status").html('<h5 style="color:red"><i class="fas fa-times-circle"></i>Final Sale</h5>');
        }
    }
    else{
        $("#status").html('<h5><i class="far fa-square"></i>Waiting</h5>');
    }
}

// check if all item checked
function checkIfFinish(){
    if (Object.keys(result).length >= number_of_item){
        return true
    }
    else{
        return false
    }
}

// Once finished
function finishRedirect(){

    $.ajax({
        contentType : 'application/json',
        data: JSON.stringify(result),
        error: function(response){
            alert('failed, there is an unknown error');
        },
        success:function(response){
            alert('finished! you can close this page');
            $('body').html("<h3> You have finished checking this cart. <br> Please close this window. </h3>")
        },
        type: 'POST',
        url: '/order_management/submit_final_sale_check/'
      })
}

