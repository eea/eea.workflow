//
// Replaces the uids in the workflow history with links to the originals
//
(function($) {
function set_resolveuids(){
	$(".reviewHistory span:contains('uid:')").each(function(){
		var text = $(this).text();
		var uid_start = text.lastIndexOf("(uid:");
		var uid_end = text.lastIndexOf(")");
		var uid = text.slice(uid_start + 5, uid_end);
		var msg = text.slice(0, uid_start);

		var base = $('body').data('base-url') || $("base").attr('href') || document.baseURI || window.location.href.split("?")[0];
		var node = $("<a>").attr('href', base+'/resolveuid/' + uid).text("original");
		var div = $("<span>").text(msg);
		div.append(node);
		$(this).html(div);
	});
}

$(document).ready(set_resolveuids);

})(jQuery);
