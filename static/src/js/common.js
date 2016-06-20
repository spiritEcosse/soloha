/**
 * Created by igor on 16.01.16.
 */

$(document).ready(function() {
    $('.stop-propagation').click(function(event){
        event.stopPropagation();
    });

    $(".dropdown-menu li").bind({
        keydown: function(e) {
            var key = e.keyCode;
            var target = $(e.currentTarget);

            switch(key) {
                case 38: // arrow up
                    target.prev().focus();
                    break;
                case 40: // arrow down
                    target.next().focus();
                    break;
            }
        },

        focusin: function(e) {
            $(e.currentTarget).addClass("selected");
        },

        focusout: function(e) {
            $(e.currentTarget).removeClass("selected");
        }
    });

    $('#categories a[role="tab"]').click(function (e) {
        e.preventDefault();
        $(this).tab('show')
    })
});