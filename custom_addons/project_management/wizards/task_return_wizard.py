from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError
import logging

_logger = logging.getLogger(__name__)

class TaskReturnWizard(models.TransientModel):
    _name = 'project.task.return.wizard'
    _description = 'Wizard to Return Task to Developer with Reason'

    return_reason = fields.Text(string='Reason for Returning Task', required=True)

    def action_return(self):
        active_ids = self.env.context.get('active_ids')
        tasks = self.env['project.tasks'].browse(active_ids)
        for task in tasks:
            # save return reason to tasks model
            task.return_reason = self.return_reason
            task.action_return_to_dev()
            _logger.info('Task "%s" has been returned to Dev by %s. Reason: %s', task.name, self.env.user.name, self.return_reason)
        return {'type': 'ir.actions.act_window_close'}