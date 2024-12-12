from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Sprint(models.Model):
    _name = 'project.sprint'
    _description = 'Project Sprint'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sprint_code = fields.Char(string='Sprint Code', readonly=True)
    name = fields.Char(string='Sprint Name', required=True)
    project_id = fields.Many2one('project.management', string='Project', required=True, ondelete='cascade')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('close', 'Close'),
    ], string='Status', default='draft', tracking=True)
    task_ids = fields.One2many('project.tasks', 'sprint_id', string='Tasks')
    
    @api.onchange('start_date', 'end_date')
    def _onchange_date(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            return {
                'warning': {
                    'title': _('Invalid Date'),
                    'message': _('The end date must be greater than the start date. Please correct the dates.'),
                }
            }
            
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(_('Start Date must be before End Date.'))
            
    @api.model
    def create(self, vals):
        if vals.get('sprint_code', 'New') == 'New':
            vals['sprint_code'] = self.env['ir.sequence'].next_by_code('project.sprint') or 'New'
        return super(Sprint, self).create(vals)
    
    @api.model
    def default_get(self, fields):
        res = super(Sprint, self).default_get(fields)
        if 'sprint_code' in fields:
            res['sprint_code'] = self.env['ir.sequence'].next_by_code('project.sprint') or 'New'
        return res