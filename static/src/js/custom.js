/**
 * Created by igor on 16.01.16.
 */

$(document).ready(function() {
     $('.lightSlider').lightSlider({
         item:4,
         loop:true,
         slideMove:1,
         slideMargin:0,
         pager: false
    });

    $('.lightSlider_tree').lightSlider({
         item:3,
         loop:true,
         slideMove:1,
         slideMargin:0,
         pager: false
    });

    // $('#link_news').click(function(){
    //     slider.refresh();
    // });
    //
    // $('#link_hits').click(function(){
    //     slider.refresh();
    // });
    //
    // $('#link_special').click(function(){
    //     slider.refresh();
    // });
    //
    // $('#recommended-tab').click(function(){
    //     slider.refresh();
        
    // });
});
