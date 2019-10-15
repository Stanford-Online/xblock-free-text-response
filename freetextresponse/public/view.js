/* eslint-disable no-unused-vars */
/**
 * Initialize the FreeTextResponse student view
 * @param {Object} runtime - The XBlock JS Runtime
 * @param {Object} element - The containing DOM element for this instance of the XBlock
 * @returns {undefined} nothing
 */
function FreeTextResponseView(runtime, element) {
    /* eslint-enable no-unused-vars */
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

    if (typeof $xblocksContainer.data(cachedAnswerId) !== 'undefined') {
        textareaStudentAnswer.text($xblocksContainer.data(cachedAnswerId));
        problemProgress.text($xblocksContainer.data(problemProgressId));
        usedAttemptsFeedback.text($xblocksContainer.data(usedAttemptsFeedbackId));
    }

    // POLYFILL notify if it does not exist. Like in the xblock workbench.
    runtime.notify = runtime.notify || function () {
        // eslint-disable-next-line prefer-rest-params, no-console
        console.log('POLYFILL runtime.notify', arguments);
    };

    /**
     * Update CSS classes
     * @param {string} newClass - a CSS class name to be used
     * @returns {undefined} nothing
     */
    function setClassForTextAreaParent(newClass) {
        textareaParent.removeClass('correct');
        textareaParent.removeClass('incorrect');
        textareaParent.removeClass('unanswered');
        textareaParent.addClass(newClass);
    }

    /**
     * Convert list of responses to an html string
     * @param {Array} responses - a list of Responses
     * @returns {string} a string of HTML to add to the page
     */
    function getStudentResponsesHtml(responses) {
        var html = '';
        var noResponsesText = responseList.data('noresponse');
        responses.forEach(function (item) {
            html += '<li class="other-student-responses">' + item.answer + '</li>';
        });
        html = html || '<li class="no-response">' + noResponsesText + '</li>';
        return html;
    }

    /**
     * Display responses, if applicable
     * @param {Object} response - a jQuery HTTP response
     * @returns {undefined} nothing
     */
    function displayResponsesIfAnswered(response) {
        if (!response.display_other_responses) {
            $element.find('.responses-box').addClass('hidden');
            return;
        }
        var responseHTML = getStudentResponsesHtml(response.other_responses);
        responseList.html(responseHTML);
        $element.find('.responses-box').removeClass('hidden');
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
            state: 'start',
        });
        $.ajax(url, {
            type: 'POST',
            data: JSON.stringify({
                // eslint-disable-next-line camelcase
                student_answer: $element.find('.student_answer').val(),
                // eslint-disable-next-line camelcase
                can_record_response: $element.find('.messageCheckbox').prop('checked'),
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
                    state: 'end',
                });
            },
            error: function buttonSubmitOnError() {
                runtime.notify('error', {});
            },
        });
        return false;
    });

    buttonSave.on('click', function () {
        buttonSave.text(buttonSave[0].dataset.checking);
        runtime.notify('save', {
            message: 'Saving...',
            state: 'start',
        });
        $.ajax(urlSave, {
            type: 'POST',
            data: JSON.stringify({
                // eslint-disable-next-line camelcase
                student_answer: $element.find('.student_answer').val(),
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
                    state: 'end',
                });
            },
            error: function buttonSaveOnError() {
                runtime.notify('error', {});
            },
        });
        return false;
    });

    textareaStudentAnswer.on('keydown', function () {

        // Reset Messages
        submissionReceivedMessage.text('');
        userAlertMessage.text('');
        setClassForTextAreaParent('unanswered');
    });
}
