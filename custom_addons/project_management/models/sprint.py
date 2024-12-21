from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)


from datetime import timedelta

class Sprint(models.Model):
    _name = 'project.sprint'
    _description = 'Project Sprint'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sprint_code = fields.Char(string='Sprint Code', 
                              readonly=True, 
                              default='New')
    name = fields.Char(string='Sprint Name', 
                       required=True)
    project_id = fields.Many2one('project.management', 
                                 string='Project', 
                                 ondelete='cascade')
    start_date = fields.Date(string='Start Date', 
                             tracking=True) 
    end_date = fields.Date(string='End Date', 
                           tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('close', 'Close'),
    ], string='Status', default='draft', tracking=True)
    task_ids = fields.One2many('project.tasks', 
                               'sprint_id', 
                               string='Tasks')

    # kiểm tra ngày bắt đầu
    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.project_id and self.project_id.start_date:
            # đảm bảo ngày bắt đầu phải bằng hoặc lớn hơn ngày bắt đầu dự án
            if self.start_date < self.project_id.start_date:
                self.start_date = False
                raise ValidationError(_("Sprint start date should be greater than or equal to project start date.\n"
                                        "Sprint: %s\n"
                                        "Project: %s\n"
                                        "Project Start Date: %s"
                                        ) % (self.name, self.project_id.name, self.project_id.start_date))
        
    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.start_date and self.project_id and self.project_id.start_date:
            if self.end_date:
                # đảm bảo ngày kết thúc phải bằng hoặc nhỏ hơn ngày kết thúc dự án
                if self.end_date > self.project_id.end_date:
                    self.end_date = False
                    raise ValidationError(_(
                        "Sprint end date should be less than or equal to project end date.\n"
                        "Sprint: %s\n"
                        "Project: %s\n"
                        "Project End Date: %s"
                    ) % (self.name, self.project_id.name, self.project_id.end_date))

    # đảm bảo ngày bắt đầu phải nhỏ hơn ngày kết thúc
    @api.onchange('start_date', 'end_date')
    def _check_start_must_be_less_than_end_date(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_("Sprint start date should be less than or equal to end date."))

    # đảm bảo tại một thời điểm chỉ có một sprint được mở
    @api.onchange('state')
    def _check_overlap_sprint(self):
        if self.state == 'open':
            open_sprint = self.env['project.sprint'].search([('project_id', '=', self.project_id.id), 
                                                             ('state', '=', 'open'), 
                                                             ('end_date', '>=', self.start_date)], 
                                                             limit=1)
            if open_sprint:
                raise ValidationError(_(
                                    "There is already an open sprint for this project.\n"
                                    "Current Sprint: %s\n"
                                    "Project: %s\n"
                                    "Overlapping Sprint: %s\n"
                                    "Overlapping Sprint Start Date: %s\n"
                                    "Overlapping Sprint End Date: %s"
                                ) % (self.name, self.project_id.name, open_sprint.name, open_sprint.start_date, open_sprint.end_date))

    # Override create method for sprint_code sequence
    @api.model
    def create(self, vals):
        if vals.get('sprint_code', 'New') == 'New':
            vals['sprint_code'] = self.env['ir.sequence'].next_by_code('project.sprint') or 'New'
        return super(Sprint, self).create(vals)

    # Method to get open sprint (unchanged)
    @api.model
    def get_open_sprint(self, project_id):
        try:
            sprint = self.env['project.sprint'].search([('project_id', '=', project_id), ('state', '=', 'open')], limit=1)
            if not sprint:
                return {}
            return {
                'sprint_id': sprint.id,
                'sprint_name': sprint.name,
            }
        except Exception as e:
            # Log the exception
            _logger.error("Error fetching open sprint: %s", e)
            # Raise a user-friendly error
            raise UserError("An error occurred while fetching the open sprint. Please try again later.")