/**
 * Created by igor on 16.01.16.
 */

$(document).ready(function() {
    slider = $('.lightSlider').lightSlider({
        item:4,
        loop:true
    });

    $('#link_news').click(function(){
        slider.refresh();
    });

    $('#link_hits').click(function(){
        slider.refresh();
    });

    $('#link_special').click(function(){
        slider.refresh();
    });

    $('#recommended-tab').click(function(){
        slider.refresh();
    });
});