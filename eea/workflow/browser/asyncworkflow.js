/* EXTERNAL DEPENDENCIES:
 * plone_javascript_variables.js context_url
 * dropdown.js initializeMenus
 *  */

function AsyncWorkflow() {
    this.handler = "@@workflow_menu";
    this.ajaxhandler = window.context_url + '/' + this.handler;
    this.menu = jQuery("#plone-contentmenu-workflow");
    this.menuHeader = jQuery(".actionMenuHeader", this.menu);
    this.submenu = jQuery(".actionMenuContent", this.menu);
    this.actionsMenu = jQuery(".contentActions");
    this.loadingImg = "<img src='" + window.context_url + "/eea-ajax-loader.gif' " +
        "alt='Changing state ...' title='Changing state ...' />";
}

AsyncWorkflow.Events = {};
AsyncWorkflow.Events.WORKFLOW_MENU_REFRESHED = "ID-WORKFLOW_MENU_REFRESHED";

AsyncWorkflow.prototype.initialize = function() {
    var self = this;
    this.submenu.find('a').click(function(e) {
        return self.handle_click(e);
    });
};

AsyncWorkflow.prototype.handle_click = function(e) {

    // we're not sure who gets to be event target, we need the <a> link
    var $element = jQuery(e.target);
    if (e.target.nodeName !== 'A') {
        $element = $element.parent('a');
    }

    // compatibility with publishDialog and any other script that wants
    // to handle workflow action by itself
    if ($element.hasClass('kssIgnore') === true) {
        return true;
    }

    var url = $element.attr('href');
    this.submenu.hide();
    this.menuHeader.html(this.loadingImg);
    this.execute(url);
    return false;
};

AsyncWorkflow.prototype.execute = function(url) {
    var self = this;
    jQuery.post(self.ajaxhandler, {'action_url': url})
        .done(function(data) {
            self.actionsMenu.html(data);
            var messages = self.actionsMenu.find(".portalMessage").detach();
            var $kss_message = jQuery("#kssPortalMessage");
            $kss_message.next(".portalMessage").remove();
            $kss_message.after(messages);
            window.initializeMenus();    //we need to reinitialize menus
            // reinitilize async logic on new content actions
            var async = new AsyncWorkflow();
            async.initialize();
            // trigger workflow menu refreshed events
            jQuery(AsyncWorkflow.Events).trigger(AsyncWorkflow.Events.WORKFLOW_MENU_REFRESHED);
        })
        .fail(function() {
            self.menuHeader.html("Failure!");
        });
};

jQuery(document).ready(function() {
    var async = new AsyncWorkflow();
    async.initialize();
});

