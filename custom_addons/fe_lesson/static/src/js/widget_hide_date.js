odoo.define('fe_lesson.hide_date_widget', function(require) {
    "use strict";

    var FieldDate = require('web.basic_fields').FieldDate;
    var fieldRegistry = require('web.field_registry');

    var HideDateWidget = FieldDate.extend({
        className: 'o_hide_date',
        tagName: 'span',
        supportedFieldTypes: ['date'],
        events: {
            'click': '_onClickInsideWidget', // Event for clicking inside the widget
        },

        init: function() {
            this._super.apply(this, arguments);
            this._onClickOutsideWidget = this._onClickOutsideWidget.bind(this); // Bind the click outside widget event
        },

        _renderReadonly: function() {
            var formattedDate = '';
            var fullDate = '';
            if (this.value) {
                var date = new Date(this.value); // Convert the value to a Date object
                var year = date.getFullYear(); // Get the year from the Date object
                var month = ('0' + (date.getMonth() + 1)).slice(-2); // Get the month from the Date object and format it to 2 digits
                var day = ('0' + date.getDate()).slice(-2); // Get the day from the Date object and format it to 2 digits
                formattedDate = month + '/' + year; // Format 'MM/YYYY'
                fullDate = day + '/' + month + '/' + year; // Format 'DD/MM/YYYY'
            }
            this.$el.empty().append($('<span>', {
                'class': 'o_date_display readonly',
                'text': formattedDate,
                'title': fullDate, // Display tooltip with full date
            }));

            // Remove the click outside widget event
            $(document).off('click', this._onClickOutsideWidget);
        },

        _onClickInsideWidget: function(ev) {
            ev.stopPropagation(); // Prevent the click event from propagating outside the widget
        },

        _onClickOutsideWidget: function(ev) {
            if (!this.$el.has(ev.target).length) {
                this._renderReadonly(); // Switch to readonly mode when clicking outside the widget
            }
        }
    });

    fieldRegistry.add('hide_date', HideDateWidget); // Register the widget with the field registry

    return {
        HideDateWidget: HideDateWidget,
    };
});