from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Sprint(models.Model):
    _name = 'project.sprint'
    _description = 'Project Sprint'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sprint_code = fields.Char(string='Sprint Code', readonly=True, default='New')
    name = fields.Char(string='Sprint Name', required=True)
    project_id = fields.Many2one('project.management', string='Project', required=True, ondelete='cascade')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('close', 'Close'),
    ], string='Status', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('sprint_code', 'New') == 'New':
            vals['sprint_code'] = self.env['ir.sequence'].next_by_code('project.sprint') or 'New'
        return super(Sprint, self).create(vals)
    
    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            # Tìm tất cả các bản ghi có cùng tên, không phân biệt hoa thường
            duplicate_count = self.search_count([('name', '=ilike', self.name)])
            if duplicate_count > 0:
                return {
                    'warning': {
                        'title': _('Duplicate Name Warning'),
                        'message': _('The project name "{}" already exists. Please choose a different name.').format(self.name),
                    }
                }
            
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(_('Start Date must be before End Date.'))