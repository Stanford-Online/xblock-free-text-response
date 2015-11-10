function FreeTextResponseView(runtime, element) {
    'use strict';

    var $ = window.jQuery;
    var $element = $(element);
    var buttonSubmit = $element.find('.check.Submit');
    var textareaParent = $element.find('.student_answer').parent();
    var usedAttemptsFeedback = $element.find('.action .used-attempts-feedback');
    var problemProgress = $element.find('.problem-progress');
    var submitParent = $element.find('.Submit').parent();
    var wordCountError = $element.find('.word-count-error');
    var url = runtime.handlerUrl(element, 'submit');
    var userInputClass = 'user-input';

    buttonSubmit.on('click', function () {
        buttonSubmit.text('Checking...');
        runtime.notify('submit', {
            message: 'Submitting...',
            state: 'start'
        });
        $.ajax(url, {
            type: 'POST',
            data: JSON.stringify({
                'student_answer': $element.find('.student_answer').val()
            }),
            success: function buttonSubmitOnSuccess(response) {
                textareaParent.removeClass();
                textareaParent.addClass(userInputClass);
                textareaParent.addClass(response.indicator_class);
                usedAttemptsFeedback.text(response.used_attempts_feedback);
                submitParent.removeClass();
                submitParent.addClass(response.submit_class);
                problemProgress.text('(' + response.problem_progress + ')');
                wordCountError.text(response.word_count_message);
                buttonSubmit.text('Submit');

                runtime.notify('submit', {
                    state: 'end'
                });
            },
            error: function buttonSubmitOnError() {
                runtime.notify('error', {});
            }
        });
        return false;
    });
}
