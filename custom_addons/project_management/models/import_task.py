from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ImportTask(models.TransientModel):
    _name = 'import.task'
    _description = 'Import Task'

    name = fields.Char(string='Task Name', required=True)
    project_id = fields.Many2one('project.management', string='Project', required=True)
    sprint_id = fields.Many2one('project.sprint', string='Sprint')
    dev_email = fields.Char(string='Developer Email', required=True)
    qc_email = fields.Char(string='Quality Control Email', required=True)
    task_type_id = fields.Many2one('project.tasks.type', string='Task Type', required=True)
    dev_deadline = fields.Date(string='Developer Deadline')
    qc_deadline = fields.Date(string='Quality Control Deadline')
    description = fields.Text(string='Description')

    @api.model
    def create(self, vals):
        # Tạo bản ghi tạm thời trong model ảo
        record = super(ImportTask, self).create(vals)
        
        User = self.env['res.users'].sudo()
        
        # Tìm id của developer dựa trên email
        dev_user = User.search([('email', '=', vals.get('dev_email'))], limit=1)
        if not dev_user:
            raise UserError(_("No matching record found for email '%s' in field 'Developer'" % vals.get('dev_email')))
        
        # Tìm id của QC dựa trên email
        qc_user = User.search([('email', '=', vals.get('qc_email'))], limit=1)
        if not qc_user:
            raise UserError(_("No matching record found for email '%s' in field 'Quality Control'" % vals.get('qc_email')))
        
        # Chuẩn bị dữ liệu để tạo task
        task_vals = {
            'name': vals.get('name'),
            'project_id': vals.get('project_id'),
            'sprint_id': vals.get('sprint_id'),
            'dev_id': dev_user.id,
            'qc_id': qc_user.id,
            'task_type': vals.get('task_type_id'),
            'dev_deadline': vals.get('dev_deadline'),
            'qc_deadline': vals.get('qc_deadline'),
            'description': vals.get('description'),
        }

        # Create task and commit transaction
        task = self.env['project.tasks'].sudo().create(task_vals)
        _logger.info('Created and committed task: %s', task.name)
        
        return record