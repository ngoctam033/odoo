from odoo import models, fields, api

class CancelReasonWizard(models.TransientModel):
    _name = 'cancel.reason.wizard'
    _description = 'Cancel Reason Wizard'

    reason = fields.Text(string='Cancel Reason', required=True)

    def action_cancel(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        if active_ids:
            request_records = self.env['request.open.project'].browse(active_ids)
            request_records.write({
                'state': 'canceled',
                'cancel_reason': self.reason
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Requests have been canceled successfully.',
                'type': 'success',  # Các loại: 'success', 'warning', 'danger', 'info'
                'sticky': False,
            }
        }