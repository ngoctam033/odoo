odoo.define('fe_lesson.feedback_snippet', function (require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function () {
        $('#feedback_form').on('submit', function (e) {
            e.preventDefault(); // Ngăn chặn hành vi gửi form mặc định

            // Thu thập dữ liệu từ form
            var description = $('#description').val().trim();

            // Kiểm tra dữ liệu trước khi gửi
            if (!description) {
                $('#feedback_response')
                    .removeClass('success')
                    .addClass('error')
                    .text('Description is required')
                    .show();
                return;
            }

            // Gửi dữ liệu qua AJAX tới endpoint /feedback/submit
            ajax.jsonRpc('/feedback/submit', 'call', {
                description: description
            }).then(function (response) {
                if (response.status === 'success') {
                    // Hiển thị thông báo thành công
                    $('#feedback_response')
                        .removeClass('error')
                        .addClass('success')
                        .text(response.message)
                        .show();
                    
                    // Làm sạch form
                    $('#feedback_form')[0].reset();
                } else {
                    // Hiển thị thông báo lỗi
                    $('#feedback_response')
                        .removeClass('success')
                        .addClass('error')
                        .text(response.message)
                        .show();
                }
            }).catch(function (error) {
                // Xử lý lỗi mạng hoặc server
                $('#feedback_response')
                    .removeClass('success')
                    .addClass('error')
                    .text('An error occurred while submitting your feedback. Please try again.')
                    .show();
                console.error(error);
            });
        });
    });
});