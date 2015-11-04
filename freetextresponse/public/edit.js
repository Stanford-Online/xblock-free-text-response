function FreeTextResponseEdit(runtime, element) {
    var $ = window.$;
    var $element = $(element);
    var buttonSave = $element.find('.save-button');
    var buttonCancel = $element.find('.cancel-button');
    var url = runtime.handlerUrl(element, 'studio_view_save');

    buttonCancel.on('click', function () {
        runtime.notify('cancel', {});
        return false;
    });

    buttonSave.on('click', function () {
        runtime.notify('save', {
            message: 'Saving...',
            state: 'start'
        });
        $.ajax(url, {
            type: 'POST',
            data: JSON.stringify({
                'display_name': $('#freetextresponse_display_name').val(),
                'prompt': $('#freetextresponse_prompt').val(),
                'weight': $('#freetextresponse_weight').val(),
                'max_attempts': $('#freetextresponse_max_attempts').val(),
                'display_correctness': $('#freetextresponse_display_correctness').val(),
                'min_word_count': $('#freetextresponse_min_word_count').val(),
                'max_word_count': $('#freetextresponse_max_word_count').val(),
                'fullcredit_keyphrases': $('#freetextresponse_fullcredit_keyphrases').val(),
                'halfcredit_keyphrases': $('#freetextresponse_halfcredit_keyphrases').val()
            }),
            success: function buttonSaveOnSuccess() {
                runtime.notify('save', {
                    state: 'end'
                });
            },
            error: function buttonSaveOnError() {
                runtime.notify('error', {});
            }
        });
        return false;
    });
}
