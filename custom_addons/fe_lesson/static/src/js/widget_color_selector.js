odoo.define('fe_lesson.color_integer_widget', function(require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');

    var ColorPickerWidget = AbstractField.extend({
        className: 'o_int_color',
        tagName: 'span',
        supportedFieldTypes: ['integer'],
        events: {
            'click .o_color_display': '_onClickColorDisplay', // Event for clicking on the color display element
            'click .o_color_option': '_onClickColorOption', // Event for clicking on a color option
            'click': '_onClickInsideWidget', // Event for clicking inside the widget
        },

        init: function() {
            this.totalColors = 15; // Total number of available colors
            this.colors = [
                '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', 
                '#00FFFF', '#800000', '#808000', '#008080', '#800080',
                '#808080', '#C0C0C0', '#FFA07A', '#20B2AA', '#FFFFFF',
            ]; // List of colors
            this._super.apply(this, arguments);
            this._onClickOutsideWidget = this._onClickOutsideWidget.bind(this); // Bind the click outside widget event
        },

        _renderEdit: function() {
            this.$el.empty(); // Clear the current content of the widget
            var $colorList = $('<div>', {'class': 'o_color_list'}); // Create a container for the color list
            for (let i = 0; i < this.totalColors; i++) {
                var isActive = (this.value === i) ? ' active' : ''; // Check if the current color is selected
                var $colorOption = $('<span>', {
                    'class': 'o_color_option' + isActive,
                    'data-val': i,
                    'style': 'background-color: ' + this.colors[i],
                }); // Create a color option element
                if (isActive) {
                    $colorOption.append($('<i>', {
                        'class': 'fa fa-check check-icon'
                    })); // Add a check icon if the color is selected
                }
                $colorList.append($colorOption); // Add the color option to the list
            }
            this.$el.append($colorList); // Add the color list to the widget

            // Display the count of selected colors
            this._renderColorCount();

            // Add the click outside widget event
            $(document).on('click', this._onClickOutsideWidget);
        },

        _renderReadonly: function() {
            var color = this.colors[this.value] || '#FFFFFF'; // Get the current color or default to white if not set
            this.$el.empty().append($('<span>', {
                'class': 'o_color_display readonly',
                'style': 'background-color: ' + color,
            })); // Display the current color

            // Display the count of selected colors
            this._renderColorCount();

            // Remove the click outside widget event
            $(document).off('click', this._onClickOutsideWidget);
        },

        _countSelectedColors: function() {
            var self = this;
            return this._rpc({
                model: 'my.model', // Replace 'my.model' with your model name
                method: 'search_read',
                args: [[['color', '!=', false]], ['color']],
            }).then(function(records) {
                // Get the list of unique colors that have been used
                var usedColors = _.uniq(_.map(records, 'color'));
                return usedColors.length; // Return the count of selected colors
            });
        },

        _renderColorCount: function() {
            var self = this;
        
            // Query the database to count the number of selected colors
            this._countSelectedColors().then(function(count) {
                // Remove the old color count element if it exists
                self.$('.color-count').remove();
        
                // Only add the color count element when in form view mode
                if (self.mode === 'edit') {
                    // Create a new color count element
                    var $colorCount = $('<div>', {
                        'class': 'color-count',
                        'text': 'Colors selected: ' + count
                    });
        
                    // Add the color count element to the widget
                    self.$el.append($colorCount);
                }
            });
        },

        _onClickColorDisplay: function(ev) {
            ev.stopPropagation(); // Prevent the click event from propagating outside the widget
            this._renderEdit(); // Switch to edit mode when clicking on the color display element
        },

        _onClickColorOption: function(ev) {
            var $target = $(ev.currentTarget);
            var data = $target.data();
            this._setValue(data.val.toString()); // Update the selected color value
            this._renderEdit(); // Re-render to update the active color
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

    fieldRegistry.add('int_color', ColorPickerWidget); // Register the widget with the field registry

    return {
        ColorPickerWidget: ColorPickerWidget,
    };
});