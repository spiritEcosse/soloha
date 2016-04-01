/**
 * Created by igor on 16.01.16.
 */

$(document).ready(function() {
    $('.dropdown-menu').click(function(event){
        event.stopPropagation();
    });

    $('#categories a').click(function (e) {
        e.preventDefault()
        $(this).tab('show')
    })
});