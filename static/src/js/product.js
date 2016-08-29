/**
 * Created by igor on 16.01.16.
 */

$(document).ready(function() {
    $('#lightSlider_product').lightSlider({
        gallery:true,
        item:1,
        vertical:true,
        verticalHeight:295,
        vThumbWidth:50,
        thumbItem:8,
        thumbMargin:4,
        slideMargin:0,
        loop:true
    });

    $( "#primary_info a" ).click(function(){
        $('html, body').animate({scrollTop: $(this.hash).offset().top}, 400);
    });

    if ($('#primary_info').length) {
        $('#primary_info').affix({
            offset: {
                top: $('#primary_info').offset().top,
                bottom: ($('#items').outerHeight(true)) + 504
            }
        });
    }
});