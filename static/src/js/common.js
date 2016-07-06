/**
 * Created by igor on 16.01.16.
 */

$(document).ready(function() {
    $('.stop-propagation').click(function(event){
        event.stopPropagation();
    });

    $('.dropdown-menu li a').click(function (e) {
        e.stopPropagation();
    });

    $('#categories a[role="tab"]').click(function (e) {
        e.preventDefault();
        $(this).tab('show')
    });
});