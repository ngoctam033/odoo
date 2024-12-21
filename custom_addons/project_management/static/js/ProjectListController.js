odoo.define('project.button.update_newest_sprint', function (require) {
    "use strict";
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var rpc = require('web.rpc');
    var Dialog = require('web.Dialog');

    var ClickListController = ListController.extend({
        buttons_template: 'project.updates_new_sprint_button',
        events: _.extend({}, ListController.prototype.events, {
            'click .o_button_update_sprint': '_onClick',
        }),

        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            var context = this.model.loadParams.context;
            var showButton = context && context.show_update_sprint_button;
        
            console.log('context', context);
            if (!showButton) {
                // Hide the button if the context key is not set
                this.$buttons.find('.o_button_update_sprint').hide();
            }
        },

        _onClick: function () {
            var self = this;
            var context = this.model.loadParams.context;
            var project_id = context.default_project_id;
            console.log('Context', context);
            console.log('Project ID', project_id);

            rpc.query({
                model: 'project.sprint',
                method: 'get_open_sprint',
                args: [project_id],
            }).then(function (result) {
                if (result.sprint_id) {
                    console.log('Result', result);
                    Dialog.confirm(self, _.str.sprintf(
                        "Bạn có đồng ý đẩy các task của sprint cũ sang sprint mới là %s?",
                        result.sprint_name
                    ), {
                        confirm_callback: function () {
                            rpc.query({
                                model: 'project.tasks',
                                method: 'update_tasks',
                                args: [result.sprint_id, project_id], // Truyền new_sprint_id
                            }).then(function (response) {
                                if (response.status === 'success') {
                                    Dialog.alert(self, response.message, {
                                        confirm_callback: function () {
                                            self.reload(); // Reload the view to see the updated tasks
                                        }
                                    });
                                } else if (response.status === 'warning') {
                                    Dialog.alert(self, response.message);
                                } else if (response.status === 'error') {
                                    Dialog.alert(self, response.message);
                                }
                            }).catch(function (error) {
                                Dialog.alert(self, "An error occurred while updating tasks. Please try again later.");
                            });
                        },
                    });
                } else {
                    Dialog.alert(self, "Không có sprint nào đang mở.");
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

odoo.define('project.approve_refuse_all', function (require) {
    "use strict";
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var rpc = require('web.rpc');

    var ClickListController = ListController.extend({
        buttons_template: 'project.approve_refuse_all_button',
        events: _.extend({}, ListController.prototype.events, {
            'click .o_button_approve_all': '_onClickApprove',
            'click .o_button_refuse_all': '_onClickRefuse',
        }),

        _onClickApprove: function () {
            var self = this;
            var context = this.model.loadParams.context;
            console.log('Context', context);
            var selectedIds = this.getSelectedIds();
            if (selectedIds.length === 0) {
                this._showNotification('Warning', 'Please select at least one record.', 'warning');
                return;
            }    
            rpc.query({
                model: context.default_model,
                method: 'approve_request',
                args: [selectedIds],
            }).then(function (result) {
                if (result.status === 'success') {
                    self._showNotification('Success', result.message, 'success');
                    self.reload();
                } else {
                    self._showNotification('Error', result.message, 'danger');
                }
            });
        },

        _onClickRefuse: function () {
            var self = this;
            var context = this.model.loadParams.context;
            var selectedIds = this.getSelectedIds();
            if (selectedIds.length === 0) {
                this._showNotification('Warning', 'Please select at least one record.', 'warning');
                return;
            }
            rpc.query({
                model: context.default_model,
                method: 'cancel_request',
                args: [selectedIds],
            }).then(function (result) {
                if (result.status === 'success') {
                    self._showNotification('Success', result.message, 'success');
                    self.reload();
                } else {
                    self._showNotification('Error', result.message, 'danger');
                }
            });
        },
        
        _showNotification: function (title, message, type) {
            this.do_notify(title, message, type);
        },
    });

    var ClickListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: ClickListController,
        }),
    });

    viewRegistry.add('project.approve_refuse_all', ClickListView);
});