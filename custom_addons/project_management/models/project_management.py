from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError

from datetime import timedelta

class ProjectManagement(models.Model):
    _name = 'project.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Management'
    _sql_constraints = [('check_dates', 'CHECK(start_date <= end_date)', 'End Date must be greater than Start Date.')]

    project_code = fields.Char(string='Project Code', 
                               readonly=True, 
                               default='New')
    name = fields.Char(string='Project Name', 
                       required=True)
    start_date = fields.Date(string='Start Date', 
                             required=True, 
                             tracking=True, 
                             default=fields.Date.today)
    end_date = fields.Date(string='End Date', 
                           required=True, 
                           default=fields.Date.today() + timedelta(days=90),
                           tracking=True, 
                           index=True)
    state = fields.Selection([
                                ('open', 'Open'),
                                ('close', 'Close')
                            ], string='Status of Project', 
                            default='open',
                            tracking=True)
    project_manager = fields.Many2one('res.users', 
                                      string='Project Manager', 
                                      tracking=True)
    developer_ids = fields.Many2many('res.users', 'project_management_developer_rel', 
                                     string='Developer', 
                                     tracking=True)
    qc_ids = fields.Many2many('res.users', 'project_management_qc_rel', 
                              string='Quality Control', 
                              tracking=True)
    description = fields.Text(string='Description', 
                              tracking=True)
    sprint_ids = fields.One2many('project.sprint', 'project_id', 
                                 string='Sprints')
    task_ids = fields.One2many('project.tasks', 'project_id', 
                               string='Tasks')
    task_count = fields.Integer(string='Number of Tasks', 
                                compute='_compute_task_count')

    def action_view_tasks(self):
        action = self.with_context(active_id=self.id, active_ids=self.ids) \
            .env.ref('project_management.action_project_task_list') \
            .sudo().read()[0]
        action['display_name'] = self.name
        return action 

    # thêm hàm để đảm bảo task và spint phải done
    def are_all_sprints_and_tasks_done(self):
        for sprint in self.env['project.sprint'].search([('project_id', '=', self.id)]):
            if sprint.state != 'done':
                return False
            for task in self.env['project.tasks'].search([('sprint_id', '=', sprint.id)]):
                if task.state != 'done':
                    return False
        return True

    @api.depends('task_ids')
    def _compute_task_count(self):
        for project in self:
            project.task_count = len(project.task_ids)

    @api.constrains('name')
    def _check_duplicate_name(self):
        for record in self:
            if record.name:
                duplicate_count = self.search_count([('name', '=ilike', record.name)])
                if duplicate_count > 1:
                    raise ValidationError(_('The project name "{}" already exists. Please choose a different name.').format(record.name))

    @api.onchange('start_date', 'end_date')
    def _onchange_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    record.end_date = record._origin.end_date
                    record.start_date = record._origin.start_date
                    raise ValidationError(_('End Date must be greater than Start Date.'))

    @api.model
    def create(self, vals):
        if vals.get('project_code', 'New') == 'New':
            vals['project_code'] = self.env['ir.sequence'].next_by_code('project_management_sequence') or 'New'
        return super(ProjectManagement, self).create(vals)

    def write(self, vals):
        pm_editable_fields = {'description', 'developer_ids', 'qc_ids', 'sprint_ids', 'task_ids'}
        if self.env.user.has_group('project_management.group_project_admin') or self.env.user.has_group('base.group_system'):
            # Project Admin và System Admin có thể chỉnh sửa toàn bộ thông tin
            return super(ProjectManagement, self).write(vals)
        elif self.env.user.has_group('project_management.group_project_pm'):
            # Project Manager chỉ có thể chỉnh sửa các trường pm_editable_fields
            unauthorized_fields = [field for field in vals if field not in pm_editable_fields]
            if unauthorized_fields:
                pm_editable_field_names = [self.fields_get(allfields=[field])[field]['string'] for field in pm_editable_fields]
                raise AccessError(_("As a Project Manager, you can only modify the following fields: %s") % ', '.join(pm_editable_field_names))
        else:
            # Các nhóm khác không có quyền chỉnh sửa
            raise AccessError(_("You do not have the rights to modify any fields."))
        return super(ProjectManagement, self).write(vals)