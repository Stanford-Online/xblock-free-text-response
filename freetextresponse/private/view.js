function FreeTextResponseView(runtime, element) {
    'use strict';

    var $ = window.jQuery;
    var $element = $(element);
    var buttonSubmit = $element.find('.check.Submit');
    var buttonSave = $element.find('.save');
    var usedAttemptsFeedback = $element.find('.action .used-attempts-feedback');
    var problemProgress = $element.find('.problem-progress');
    var submissionReceivedMessage = $element.find('.submission-received');
    var userAlertMessage = $element.find('.user_alert');
    var textareaStudentAnswer = $element.find('.student_answer');
    var textareaParent = textareaStudentAnswer.parent();

    var url = runtime.handlerUrl(element, 'submit');
    var urlSave = runtime.handlerUrl(element, 'save_reponse');

    // POLYFILL notify if it does not exist. Like in the xblock workbench.
    runtime.notify = runtime.notify || function () {
        console.log('POLYFILL runtime.notify', arguments);
    };

    function setClassForTextAreaParent(new_class) {
        textareaParent.removeClass('correct');
        textareaParent.removeClass('incorrect');
        textareaParent.removeClass('unanswered');
        textareaParent.addClass(new_class); 
    }

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
                usedAttemptsFeedback.text(response.used_attempts_feedback);
                buttonSubmit.addClass(response.nodisplay_class);
                problemProgress.text(response.problem_progress);
                submissionReceivedMessage.text(response.submitted_message);
                buttonSubmit.text('Submit');
                userAlertMessage.text(response.user_alert);
                buttonSave.addClass(response.nodisplay_class);
                setClassForTextAreaParent(response.indicator_class); 
 
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

    buttonSave.on('click', function () {
        buttonSave.text('Checking...');
        runtime.notify('save', {
            message: 'Saving...',
            state: 'start'
        });
        $.ajax(urlSave, {
            type: 'POST',
            data: JSON.stringify({
                'student_answer': $element.find('.student_answer').val()
            }),
            success: function buttonSaveOnSuccess(response) {
                buttonSubmit.addClass(response.nodisplay_class);
                buttonSave.addClass(response.nodisplay_class);
                usedAttemptsFeedback.text(response.used_attempts_feedback);
                problemProgress.text(response.problem_progress);
                submissionReceivedMessage.text(response.submitted_message);
                buttonSave.text('Save');
                userAlertMessage.text(response.user_alert);

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

    textareaStudentAnswer.on('keydown', function() {
        // Reset Messages
        submissionReceivedMessage.text('');
        userAlertMessage.text('');
        setClassForTextAreaParent('unanswered');
    });
}
