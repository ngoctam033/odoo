from odoo import api, fields, models, _
from odoo.exceptions import UserError

class EstateCancelWizard(models.TransientModel):
    _name = 'estate.cancel.wizard'
    _description = 'Estate Cancel Wizard'

    reason_cancel = fields.Text(string=_('Cancel Reason'), required=True)

    def action_cancel(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            property_record = self.env['estate.property'].browse(active_id)
            property_record.write({
                'state': 'canceled',
                'reason_cancel': self.reason_cancel
            })
        else:
            raise UserError(_('No active property record found to cancel.'))