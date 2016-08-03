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

    $('button[data-loading-text]')
    .on('click', function () {
        var btn = $(this);
        btn.button('loading');
    });

    // $('.selectpicker').selectpicker({
    //     style: 'btn-info',
    //     size: 4
    // });
});