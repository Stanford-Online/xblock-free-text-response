function FreeTextResponseView(runtime, element) {
    'use strict';

    var $ = window.jQuery;
    var $element = $(element);
    var buttonSubmit = $element.find('.check.Submit');
    var buttonSave = $element.find('.save');
    var buttonHint = $element.find('.hint');
    var usedAttemptsFeedback = $element.find('.action .used-attempts-feedback');
    var problemProgress = $element.find('.problem-progress');
    var submissionReceivedMessage = $element.find('.submission-received');
    var userAlertMessage = $element.find('.user_alert');
    var textareaStudentAnswer = $element.find('.student_answer');
    var textareaParent = textareaStudentAnswer.parent();
    var message = $element.find('.message');
    var feedback = $element.find('.feedback');
    var feedbackLabel = $element.find('.feedback-label');
    var feedbackText = $element.find('.feedback-text');
    var hintText = $element.find('.hint-text');
   
    var url = runtime.handlerUrl(element, 'submit');
    var urlSave = runtime.handlerUrl(element, 'save_response');
    var urlHint = runtime.handlerUrl(element, 'hint_reponse');


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
                buttonSubmit.addClass(response.submitdisplay_class);
                problemProgress.text(response.problem_progress);
                submissionReceivedMessage.text(response.submitted_message);
                buttonSubmit.text('Submit');
                userAlertMessage.text(response.user_alert);
                buttonSave.addClass(response.submitdisplay_class);
                setClassForTextAreaParent(response.indicator_class); 
                feedbackLabel.text(response.feedback_label);
                feedbackText.text(response.feedback_text);
                // Feedback is only changed in on submission 
                feedback.removeClass('correct');
                feedback.removeClass('incorrect');
                feedback.removeClass('unanswered');
                feedback.addClass(response.indicator_class); 
                hintText.text('');

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
                buttonSubmit.addClass(response.submitdisplay_class);
                buttonSave.addClass(response.submitdisplay_class);
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

    buttonHint.on('click', function () {
        runtime.notify('hint', {
            message: 'Hint',
            state: 'start'
        });
        $.ajax(urlHint, {
            type: 'POST',
            data: JSON.stringify({}),
            success: function buttonHintOnSuccess(response) {
                hintText.text(response.hint_text);
                
                runtime.notify('hint', {
                    state: 'end'
                });
            },
            error: function buttonHintOnError() {
                runtime.notify('error', {});
            }
        });
        return false;
    });

    textareaStudentAnswer.on('keydown', function() {
        // Reset Messages
        submissionReceivedMessage.text('');
        //userAlertMessage.text('');
        setClassForTextAreaParent('unanswered');
    });
}
