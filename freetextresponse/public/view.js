function FreetextresponseView(runtime, element) {
    'use strict';

    var $ = window.jQuery;
    var $element = $(element);
    var buttonSubmit = $element.find('.check.Submit');
    var textareaParent = $element.find('.student_answer').parent();
    var usedAttemptsFeedback = $element.find('.action .used_attempts_feedback');
    var problemProgress = $element.find('.problem-progress');
    var submitParent = $element.find('.Submit').parent();
    var wordCountError = $element.find('.word-count-error');
    var url = runtime.handlerUrl(element, 'submit');

    buttonSubmit.on('click', function () {
        console.log('submit button was pressed!');
        buttonSubmit.text('Checking...');
        runtime.notify('submit', {
            message: 'Submitting...',
            state: 'start',
        });
        $.ajax(url, {
            type: 'POST',
            data: JSON.stringify({
                'student_answer': $element.find('.student_answer').val(),
            }),
            success: function buttonSubmitOnSuccess(response) {
                console.log("The response is ", response);
                textareaParent.removeClass();
                textareaParent.addClass(response.indicator_class);
                usedAttemptsFeedback.text(response.used_attempts_feedback);
                submitParent.removeClass();
                submitParent.addClass(response.submit_class);
                problemProgress.text('(' + response.problem_progress + ')');
                wordCountError.text(response.word_count_message);
                buttonSubmit.text('Submit');

                runtime.notify('submit', {
                    state: 'end',
                });
            },
            error: function buttonSubmitOnError() {
                runtime.notify('error', {});
            }
        });
        return false;
    });
}
