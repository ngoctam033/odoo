from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectManagement(models.Model):
    _name = 'project.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Management'

    # Mã dự án
    project_code = fields.Char(string='Project Code', 
                               readonly=True)
    # Tên dự án
    name = fields.Char(string='Project Name', 
                       required=True)
    # ngày bắt đầu
    start_date = fields.Date(string='Start Date')
    # ngày kết thúc
    end_date = fields.Date(string='End Date', 
                           tracking=True, 
                           index=True)
    # trạng thái dự án (mở hoặc đóng)
    state = fields.Selection([
                                ('open', 'Open'),
                                ('close', 'Close'),
                            ], string='Status', 
                            default='open', 
                            tracking=True)
    # project manager
    project_manager = fields.Many2one('res.users', 
                                      string='Project Manager', 
                                      tracking=True)
    # developer
    developer_ids = fields.Many2many('res.users', 
                                     'project_management_developer_rel', 
                                     string='Developer', 
                                     tracking=True)
    # Quality Control
    qc_ids = fields.Many2many('res.users', 
                              'project_management_qc_rel', 
                              string='Quality Control', 
                              tracking=True)
    # Mô tả dự án
    description = fields.Text(string='Description', 
                              tracking=True)
    
    # Tạo quan hệ giữa bảng project.management và bảng project.sprint
    sprint_ids = fields.One2many('project.sprint', 
                                 'project_id', 
                                 string='Sprints')
    
    # add task_ids field
    task_ids = fields.One2many('project.tasks', 
                               'project_id', 
                               string='Tasks')

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
            if record.start_date and record.end_date and record.start_date >= record.end_date:
                raise ValidationError(_("The end date must be greater than the start date. Please correct the dates."))

    @api.onchange('name')
    def _onchange_name(self):
        for record in self:
            if record.name:
                # Find all records with the same name
                duplicate_count = self.search_count([('name', '=ilike', record.name)])
                print('duplicate_count ', duplicate_count)
                if duplicate_count > 0:
                    return {
                        'warning': {
                            'title': _('Duplicate Name Warning onchange'),
                            'message': _('The property type name "{}" already exists. Please choose a different name.').format(record.name),
                        }
                    }

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            if record.name:
                # find all records with the same name(not case sensitive)
                duplicate_count = self.search_count([('name', '=ilike', record.name)])
                if duplicate_count > 1:
                    raise ValidationError(_('The property type name "{}" already exists. Please choose a different name.').format(record.name))
                    
    @api.model
    def default_get(self, fields):
        res = super(ProjectManagement, self).default_get(fields)
        if 'project_code' in fields:
            res['project_code'] = self.env['ir.sequence'].next_by_code('project_management_sequence') or 'New'
        return res
         
    @api.model
    def create(self, vals):
        if vals.get('project_code', 'New') == 'New':
            vals['project_code'] = self.env['ir.sequence'].next_by_code('project_management_sequence') or 'New'
        return super(ProjectManagement, self).create(vals)