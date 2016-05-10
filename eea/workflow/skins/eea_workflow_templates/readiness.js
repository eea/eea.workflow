/* EXTERNAL DEPENDENCIES: jquery-ui.js accordion */
function set_readiness_accordion(){
(function($) {
    $(".readiness_accordion").accordion({
        autoHeight:false
    });
})(jQuery);
}
jQuery(document).ready(set_readiness_accordion);
