/**
 * Created by igor on 16.01.16.
 */

$(document).ready(function() {
    slider = $('.lightSlider').lightSlider({
        item:4,
        loop:true
    });

    setTimeout(function(){
        slider.refresh();
    }, 1000);

    $('#link_news').click(function(){
        slider.refresh();
    });

    $('#link_hits').click(function(){
        slider.refresh();
    });

    $('#link_special').click(function(){
        slider.refresh();
    });

    $('#link_recommends').click(function(){
        slider.refresh();
    });

    $('#recommended_href').click(function() {
        $('#recommended').focus();
    });

    $('.dropdown-menu').click(function(event){
        event.stopPropagation();
    });
});