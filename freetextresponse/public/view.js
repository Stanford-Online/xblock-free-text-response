function FreeTextResponseView(runtime, element) {
    'use strict';

    var $ = window.jQuery;
    var $element = $(element);
    var $xblocksContainer = $('#seq_content');
    var buttonHide = $element.find('.hide-button');
    var buttonHideTextHide = $('.hide', buttonHide);
    var buttonHideTextShow = $('.show', buttonHide);
    var buttonSubmit = $element.find('.check.Submit');
    var buttonSave = $element.find('.save');
    var usedAttemptsFeedback = $element.find('.action .used-attempts-feedback');
    var problemProgress = $element.find('.problem-progress');
    var submissionReceivedMessage = $element.find('.submission-received');
    var userAlertMessage = $element.find('.user_alert');
    var textareaStudentAnswer = $element.find('.student_answer');
    var textareaParent = textareaStudentAnswer.parent();
    var responseList = $element.find('.response-list');
    var url = runtime.handlerUrl(element, 'submit');
    var urlSave = runtime.handlerUrl(element, 'save_reponse');

    var xblockId = $element.attr('data-usage-id');
    var cachedAnswerId = xblockId + '_cached_answer';
    var problemProgressId = xblockId + '_problem_progress';
    var usedAttemptsFeedbackId = xblockId + '_used_attempts_feedback';
    if ($xblocksContainer.data(cachedAnswerId) !== undefined) {
        textareaStudentAnswer.text($xblocksContainer.data(cachedAnswerId));
        problemProgress.text($xblocksContainer.data(problemProgressId));
        usedAttemptsFeedback.text($xblocksContainer.data(usedAttemptsFeedbackId));
    }

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

    buttonHide.on('click', function () {
        responseList.toggle();
        buttonHideTextHide.toggle();
        buttonHideTextShow.toggle();
    });

    buttonSubmit.on('click', function () {
        buttonSubmit.text(buttonSubmit[0].dataset.checking);
        runtime.notify('submit', {
            message: 'Submitting...',
            state: 'start'
        });
        $.ajax(url, {
            type: 'POST',
            data: JSON.stringify({
                'student_answer': $element.find('.student_answer').val(),
                'can_record_response': $element.find('.messageCheckbox').prop('checked')
            }),
            success: function buttonSubmitOnSuccess(response) {
                usedAttemptsFeedback.text(response.used_attempts_feedback);
                buttonSubmit.addClass(response.nodisplay_class);
                problemProgress.text(response.problem_progress);
                submissionReceivedMessage.text(response.submitted_message);
                buttonSubmit.text(buttonSubmit[0].dataset.value);
                userAlertMessage.text(response.user_alert);
                buttonSave.addClass(response.nodisplay_class);
                setClassForTextAreaParent(response.indicator_class);
                displayResponsesIfAnswered(response);

                $xblocksContainer.data(cachedAnswerId, $element.find('.student_answer').val());
                $xblocksContainer.data(problemProgressId, response.problem_progress);
                $xblocksContainer.data(usedAttemptsFeedbackId, response.used_attempts_feedback);

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

    function getStudentResponsesHtml(responses) {
        /*
        Convert list of responses to a html string to add to the page
        */
        var html = '';
        var noResponsesText = responseList.data('noresponse');
        responses.forEach(function(item) {
            html += '<li class="other-student-responses">' + item.answer + '</li>';
        });
        html = html || '<li class="no-response">' + noResponsesText + '</li>';
        return html;
    }

    function displayResponsesIfAnswered(response) {
        if (!response.display_other_responses) {
            $element.find('.responses-box').addClass('hidden');
            return;
        }
        var responseHTML = getStudentResponsesHtml(response.other_responses);
        responseList.html(responseHTML);
        $element.find('.responses-box').removeClass('hidden');
    }

    buttonSave.on('click', function () {
        buttonSave.text(buttonSave[0].dataset.checking);
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
                buttonSave.text(buttonSave[0].dataset.value);
                userAlertMessage.text(response.user_alert);

                $xblocksContainer.data(cachedAnswerId, $element.find('.student_answer').val());
                $xblocksContainer.data(problemProgressId, response.problem_progress);
                $xblocksContainer.data(usedAttemptsFeedbackId, response.used_attempts_feedback);

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
