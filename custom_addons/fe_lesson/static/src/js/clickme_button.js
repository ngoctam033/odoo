odoo.define('fe_lesson.clickme.button', function (require) {
    "use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var QWeb = core.qweb;
    var _t = core._t;

    var ClickMeListController = ListController.extend({
        buttons_template: 'fe_lesson.buttons',
        events: _.extend({}, ListController.prototype.events, {
            'click .o_button_clickme': '_onClickMe', // Event for the "Click Me" button
            'click .o_button_apply': '_onApply', // Event for the "Apply" button
            'click .o_button_clear': '_onClear', // Event for the "Clear" button
            'change .custom-checkbox-input': '_onCheckboxChange', // Event for the "Toggle Column" checkbox
        }),

        _onClickMe: function () {
            this.do_notify(
                _t("Inventory Overview added to dashboard"),
                _t("Please refresh your browser for the changes to take effect.")
            );
        },

        _onApply: function () {
            var self = this;
            // Find all elements with the class 'custom-checkbox-input'
            this.$el.find('.custom-checkbox-input').each(function() {
                var $checkbox = $(this);
                // Check if the checkbox is checked
                var isChecked = $checkbox.is(':checked');
                // Get the column index from the data attribute
                var columnIndex = $checkbox.data('column-index');
                // Call the function to toggle the visibility of the column
                self._toggleColumnVisibility(columnIndex, isChecked);
            });
            // hide o_button_apply class
            this.$el.find('.o_button_apply').hide();
        },

        _onClear: function () {
            // Uncheck all checkboxes with the class 'custom-checkbox-input'
            this.$el.find('.custom-checkbox-input').prop('checked', false);
            
            // Iterate over each row in the table and show all columns
            this.$el.find('table tr').each(function() {
                $(this).find('td, th').show(); // Show all columns
            });

            // Hide the Apply and Clear buttons
            this.$el.find('.o_button_apply').hide();
            this.$el.find('.o_button_clear').hide();
        },

        _onCheckboxChange: function () {
            // Always show the Apply button when any checkbox state changes
            this.$el.find('.o_button_apply').show();
        
            // Check if at least one of the specific checkboxes is checked
            var colorChecked = this.$el.find('.hide-color').is(':checked');
            var dateChecked = this.$el.find('.hide-date').is(':checked');
            if (colorChecked || dateChecked) {
                this.$el.find('.o_button_clear').show();
            } else {
                this.$el.find('.o_button_clear').hide();
            }
        },

        _toggleColumnVisibility: function(columnIndex, isVisible) {
            // Create a selector for the column based on the column index
            var selector = 'td:nth-child(' + (columnIndex + 1) + '), th:nth-child(' + (columnIndex + 1) + ')';
            
            if (isVisible) {
                // Iterate over each row in the table and hide the specified column
                this.$el.find('table tr').each(function() {
                    $(this).find(selector).hide(); // Hide the column
                });
            } else {
                // Iterate over each row in the table and show the specified column
                this.$el.find('table tr').each(function() {
                    $(this).find(selector).show(); // Show the column
                });
            }
        },
    });

    var ClickMeListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: ClickMeListController,
        }),
    });

    viewRegistry.add('clickme_buttons', ClickMeListView);
});