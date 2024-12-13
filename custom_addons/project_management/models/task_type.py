from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TaskType(models.Model):
    _name = 'project.tasks.type'
    _description = 'Task Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    type_code = fields.Char(string='Type Code', readonly=True)
    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, vals):
        if vals.get('type_code', 'New') == 'New':
            vals['type_code'] = self.env['ir.sequence'].next_by_code('project.tasks.type') or 'New'
        return super(TaskType, self).create(vals)

    @api.model
    def default_get(self, fields):
        res = super(TaskType, self).default_get(fields)
        if 'type_code' in fields:
            res['type_code'] = self.env['ir.sequence'].next_by_code('project.tasks.type') or 'New'
        return res