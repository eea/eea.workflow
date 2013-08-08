function PublishDialog(transitions){
    this.transitions = transitions || ['publish'];
}

function make_publish_text(questions){
    var text = "Self-QA:    ";
    jQuery(".question", questions).each(function(){
        var title = jQuery("h3", this).text();
        var answer = jQuery(":radio[checked]", this).val();
        var comment = jQuery("textarea", this).val();
        if (comment.length) {
            comment += "\n";
        }
        text += title + ": " + answer + ".      " + comment + ".      ";
    });
    return text;
}

function get_base(){
    var base = (window.context_url || jQuery("base").attr('href') || document.baseURI ||
                window.location.href.split("?")[0].split('@@')[0]);
    return base;
}

PublishDialog.prototype.install = function(){
    var self = this;
    jQuery(this.transitions).each(function(){
            jQuery("#workflow-transition-" + this).click(self.onclick(this));
    });
};

PublishDialog.prototype.onclick = function(transition, e){
    // this is a partial function, it curries the transition
    var transition = transition;
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

    //var now = new Date();
    //now_str = now.getFullYear() + "/" + now.getMonth() + 1 + '/' + now.getDate();
    //form.append(jQuery("<input type='hidden' name='effective_date'>").attr('value', now_str));

    jQuery("input[name='workflow_action']", self.target).attr('value', self.transition);
    $form.submit();
    this.dialog.dialog("close");
    return false;

};

PublishDialog.Window.prototype._open = function(ui){
    var self = this;
    var okbtn = self.getDialogButton('Ok');
    jQuery(okbtn).attr('disabled', 'disabled').addClass('ui-state-disabled');

    var base = get_base();
    var url = base + "/publish_dialog";

    jQuery(self.target).load(url, function(){
        var base_url = jQuery(".metadata .context_url").text();
        jQuery("#workflow-emails-placeholder").load(base_url + '/workflow_emails', function(){
            jQuery("#notice_emails .collapsibleHeader").click(
                function(){
                    jQuery(this).parent().each(
                        function(){
                            var el = jQuery(this);
                            if (el.hasClass('expandedInlineCollapsible')) {
                                el.removeClass('expandedInlineCollapsible').addClass('collapsedInlineCollapsible');
                            } else {
                                el.removeClass('collapsedInlineCollapsible').addClass('expandedInlineCollapsible');
                            }
                        }
                        );
                });
        });
        //see if all radios have a value. When they do, activate the Ok button
        jQuery(".questions input[type='radio']", self.target).change(function(){
            var questions = jQuery(".question", self.target);
            var activated = jQuery(":radio[checked]", self.target);
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
    return;
};




jQuery(document).ready(function ($) {
        var p = new PublishDialog(['publish']);
        p.install();
});
