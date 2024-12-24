odoo.define('project_management.on_click', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');
    var rpc = require('web.rpc');

    var MyClickableWidget = AbstractField.extend({
        events: _.extend({}, AbstractField.prototype.events, {
            'click': '_onClick'
        }),
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * Display button
         * @override
         * @private
         */
        _render: function () {
            var displayName = this.value;
            console.log('Display Name:', displayName);
            // Hiển thị thông tin từ value
            this.$el.text(displayName);
            this.$el.attr('title', displayName);
            this.$el.attr('aria-label', displayName); 
        },
            /**
         * Override isEmpty to ensure 0 is not considered empty o_field_empty
         * @override
         * @private
         */
        isEmpty: function () {
            return (this.value === undefined || this.value === null || this.value === '');
        },
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
    
        /**
         * Open link button
         *
         * @private
         * @param {MouseEvent} event
         */
        _onClick: function (event) {
            event.stopPropagation();
            var self = this;
            var context = this.recordData || {};
            console.log('Context', self);
            var options = this.nodeOptions || {};
            var modelName = options.model || self.model
            var methodName = options.method || 'default_method';
            var recordId = context.id;
            console.log('Calling method:', methodName, 'on model:', modelName, 'with record ID:', this.res_id);
            rpc.query({
                model: modelName,
                method: methodName,
                args: [[recordId]],
            }).then(function (result) {
                self.do_action(result);
            }).catch(function (error) {
                console.warn('RPC call failed:', error);
            });
        },
    });

    fieldRegistry.add('on_click', MyClickableWidget);
});