$(function() {

    var _mask1 = {
        color: '#000',
        loadSpeed: 500,
        opacity: 0.5
    }

    var _mask2 = {
        color: '#999',
        loadSpeed: 500,
        opacity: 0.5
    }
    // if the function argument is given to overlay,
    // it is assumed to be the onBeforeLoad event listener
    $("a[rel].external").overlay({

        mask:_mask1,
        effect: 'apple',

        onBeforeLoad: function() {

            var wrap = this.getOverlay().find(".contentWrap");
            wrap.load(this.getTrigger().attr("href"));
        }

    });

    $("a[rel].facebox").overlay({
            top:100,
            mask: _mask2,
            closeOnClick: false
    });

    $("a[rel].message").overlay({
        top:50,
        left:$(window).width()-450,
        mask:{opacity: 0},
        onLoad: function() {
            setTimeout("$(document).click()",4000)
        }

    });







});


function show_alert(header, mess){

    d=document.createElement('div');
    $(d).addClass("message_back")
        .html("<h4>"+header+"</h4>"+mess)
        .appendTo("body")
        .overlay({
            top:50,
            left:$(window).width()-450,
            mask:{opacity: 0},
            load: true,
            onLoad: function() {
                setTimeout("$(document).click(); $(d).remove()",4000)
            }

        });



}