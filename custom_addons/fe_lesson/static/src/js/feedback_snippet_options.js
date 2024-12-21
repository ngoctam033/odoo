// static/src/js/feedback_snippet_options.js
odoo.define('fe_lesson.feedback_snippet_options', function (require) {
    'use strict';
    
    const options = require('web_editor.snippets.options');
    
    options.registry.FeedbackSnippetOptions = options.Class.extend({
        /**
         * Xử lý thay đổi màu nền
         */
        on_background_color_change: function (previewMode, value, $option) {
            this.$target.css('background-color', value);
        },

        /**
         * Xử lý thay đổi kiểu nút Submit
         */
        on_submit_button_style_change: function (previewMode, value, $option) {
            const $button = this.$target.find('button[type="submit"]');
            $button.removeClass('btn-primary btn-secondary btn-success btn-danger')
                   .addClass(value);
        },
    });
});