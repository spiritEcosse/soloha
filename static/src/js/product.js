/**
 * Created by igor on 16.01.16.
 */

$(document).ready(function() {
    $('.lightSlider').lightSlider({
        item:4,
        loop:true
    });

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

    $('.dropdown-menu').click(function(event){
        event.stopPropagation();
    });
});