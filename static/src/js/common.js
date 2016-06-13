/**
 * Created by igor on 16.01.16.
 */

$(document).ready(function() {
    $('.stop-propagation').click(function(event){
        event.stopPropagation();
    });

    $('#categories a[role="tab"]').click(function (e) {
        e.preventDefault();
        $(this).tab('show')
    })
});