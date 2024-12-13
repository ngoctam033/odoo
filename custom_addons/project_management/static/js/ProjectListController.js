odoo.define('project.button.update_newest_sprint', function (require) {
    "use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var QWeb = core.qweb;
    var _t = core._t;

    var ClickListController = ListController.extend({
        buttons_template: 'project.buttons',
        events: _.extend({}, ListController.prototype.events, {
            'click .o_button_update_sprint': '_onClick',
        }),
        
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            var self = this;
            var context = this.model.loadParams.context;
            var showButton = context && context.show_update_sprint_button;

            if (showButton) {
                // Bind the click event to the button
                this.$buttons.on('click', '.o_button_update_sprint', this._onClick.bind(this));
            } else {
                // Hide the button if the context key is not set
                this.$buttons.find('.o_button_update_sprint').hide();
            }
        },

        _onClick: function () {
            var self = this;
            rpc.query({
                route: '/project_management/update_sprint',
                params: {},
            }).then(function (result) {
                if (result.status === 'success') {
                    // Reload the view to reflect changes
                    self.reload();
                    // Display success notification
                    self.displayNotification({
                        title: 'Success',
                        message: 'Incomplete tasks have been updated to the newest sprint.',
                        type: 'success',
                    });
                } else {
                    // Display error notification
                    self.displayNotification({
                        title: 'Error',
                        message: 'Failed to update tasks.',
                        type: 'danger',
                    });
                }
            });
        },
    });

    var ClickListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: ClickListController,
        }),
    });

    viewRegistry.add('project.button.update_newest_sprint', ClickListView);
});