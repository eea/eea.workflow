function PublishDialog(transitions){
    var self = this;
    this.transitions = transitions || ['publish'];
    jQuery(AsyncWorkflow.Events).bind(
            AsyncWorkflow.Events.WORKFLOW_MENU_REFRESHED,
            function(evt, data){
                self.install();
                return true;
            });
}

function make_publish_text(questions){
    var text = "Self-QA:    ";
    jQuery(".question", questions).each(function(){
        var title = jQuery("h3", this).text();
        var answer = jQuery(":checked", this).val();
        var comment = jQuery("textarea", this).val();
        if (comment.length) {
            comment += "\n";
        }
        text += title + ": " + answer + ".      " + comment + ".      ";
    });
    return text;
}

function get_base(){
    var base = (window.context_url || jQuery('body').data('base-url') || jQuery("base").attr('href') || document.baseURI ||
                window.location.href.split("?")[0].split('@@')[0]);
    return base;
}

PublishDialog.prototype.install = function(){
    var self = this;
    jQuery(self.transitions).each(function(){
        var $transition = jQuery("#workflow-transition-" + this);
        $transition.addClass('kssIgnore').click(self.onclick(this));
    });
};

PublishDialog.prototype.onclick = function(transition, e){
    // this is a partial function, it curries the transition
    var self = this;
    if (typeof(e) === "undefined") {
        return function(e){
            self.open_dialog(transition);
            return false;
        };
    }
};

PublishDialog.prototype.open_dialog = function(transition){
    var w = new PublishDialog.Window(transition);
    w.open();
};


PublishDialog.Window = function(transition){
    var $target = jQuery("#publish-dialog-target");
    if ($target.length === 0){
        $target = jQuery("<div>").appendTo("body").attr('id', 'publish-dialog-target');
    }
    this.target = $target;
    this.transition = transition;
    this.menu = jQuery("#plone-contentmenu-workflow");
};

PublishDialog.Window.prototype.open = function(){
    var self = this;
    self.dialog = jQuery(this.target).dialog({
            title:"Confirm information before publishing",
            dialogClass:'publishDialog',
            modal:true,
            resizable:true,
            width:800,
            height:700,
            open:function(ui){self._open(ui);},
            buttons:{
                    'Ok':function(e){self.handle_ok(e);},
                    'Cancel':function(e){self.handle_cancel(e);}
                    }
            }
    );
};

PublishDialog.Window.prototype.handle_cancel = function(e){
    this.dialog.dialog("close");
};

PublishDialog.Window.prototype.handle_ok = function(e){
    var self = this;
    var $questions_area = jQuery(".questions", this.target);

    // check if all required questions have been answered positively
    var go = true;
    jQuery(".question", this.target).each(function(){
        var q = this;
        if (jQuery(q).hasClass('required')){
            var radio = jQuery("input[value='yes']", q).get(0);
            if (radio.checked !== true) {
                jQuery("h3", q).after("<div class='notice' style='color:Black; background-color:#FFE291; " +
                    "padding:3px'>You need to answer with Yes</div>");
                jQuery(".notice", q).effect("pulsate", {times:3}, 2000,
                                            function(){jQuery('.notice', q).remove();});
                go = false;
                return false;
            }
        }
    });
    if (go === false){ return false; }

    var text = make_publish_text($questions_area);
    var $form = jQuery("form", self.target);
    jQuery("textarea#comment", self.target).val(text);
    jQuery(".questions").remove();

    jQuery("input[name='workflow_action']", self.target).attr('value', self.transition);

    jQuery.post($form.attr('action'), $form.serialize())
          .done(function(data) {
              var $response = $(data),
                  $error_msgs = $response.find('.portalMessage'),
                  $error_msg = $error_msgs.eq($error_msgs.length - 1);
              $error_msg.insertAfter($("#plone-document-byline"));
              jQuery.post(window.context_url + '/' + 'workflow_menu').done(function(data){
                  var async = new window.AsyncWorkflow();
                  async.reinitialize(data);
              });
          })
          .fail(function(ev) {
              var $response = $(ev.responseText),
                  $error_msg = $response.find('.portalMessage.error');
              $error_msg.insertBefore($("#content"));
              self.menu.html("Failure!");
          });

    this.dialog.dialog("close");
    self.menu.html("<img src='" + window.context_url + "/eea-ajax-loader.gif' " +
        "alt='Changing state ...' title='Changing state ...' />");
    return false;

};

PublishDialog.Window.prototype._open = function(ui){
    var self = this;
    var okbtn = self.getDialogButton('Ok');
    jQuery(okbtn).attr('disabled', 'disabled').addClass('ui-state-disabled');

    var base = get_base();
    var url = base + "/publish_dialog";

    jQuery(self.target).load(url, function(){
        //see if all radios have a value. When they do, activate the Ok button
        jQuery(".questions input[type='radio']", self.target).change(function(){
            var questions = jQuery(".question", self.target);
            var activated = jQuery(":checked", self.target);
            var okbtn = self.getDialogButton('Ok');
            if (questions.length === activated.length) {
                jQuery(okbtn).removeAttr('disabled').removeClass('ui-state-disabled');
            } else {
                jQuery(okbtn).attr('disabled', 'disabled').addClass('ui-state-disabled');
            }
        });

    });
};


PublishDialog.Window.prototype.getDialogButton = function(button_name) {
    var parent = jQuery(this.target).parent();  //during construction we don't have this.dialog
    var buttons = jQuery('.ui-dialog-buttonpane button', parent);
    for ( var i = 0; i < buttons.length; ++i ) {
        var $button = jQuery(buttons[i]);
        if ( $button.text() == button_name ) {
            return $button[0];
        }
    }
};


jQuery(document).ready(function ($) {
    var p = new PublishDialog(['publish']);
    p.install();
});

