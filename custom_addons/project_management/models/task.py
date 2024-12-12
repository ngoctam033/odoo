from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Task(models.Model):
    _name = 'project.task'
    _description = 'Project Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    task_code = fields.Char(string='Task Code', readonly=True, default='New')
    name = fields.Char(string='Task Name', required=True)
    project_id = fields.Many2one('project.management', string='Project', required=True, ondelete='cascade')
    sprint_id = fields.Many2one('project.sprint', string='Sprint', ondelete='set null')
    dev_id = fields.Many2one('res.users', string='Developer', ondelete='set null')
    qc_id = fields.Many2one('res.users', string='Quality Control', ondelete='set null')
    task_type = fields.Selection([
        ('feature', 'Feature'),
        ('bug', 'Bug'),
        ('improvement', 'Improvement'),
    ], string='Task Type', required=True)
    dev_deadline = fields.Date(string='Developer Deadline')
    qc_deadline = fields.Date(string='Quality Control Deadline')
    state = fields.Selection([
        ('new', 'New'),
        ('dev', 'Development'),
        ('qc', 'Quality Control'),
        ('done', 'Done'),
    ], string='Status', default='new', tracking=True)
    description = fields.Text(string='Description')

    @api.model
    def create(self, vals):
        if vals.get('task_code', 'New') == 'New':
            vals['task_code'] = self.env['ir.sequence'].next_by_code('project.task') or 'New'
        return super(Task, self).create(vals)

    @api.constrains('dev_id', 'dev_deadline', 'qc_id', 'qc_deadline')
    def _check_deadlines(self):
        for record in self:
            if record.dev_id and not record.dev_deadline:
                raise ValidationError(_('Developer Deadline is required if Developer is assigned.'))
            if record.qc_id and not record.qc_deadline:
                raise ValidationError(_('Quality Control Deadline is required if Quality Control is assigned.'))