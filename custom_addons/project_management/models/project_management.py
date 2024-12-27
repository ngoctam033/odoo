from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError

import logging
_logger = logging.getLogger(__name__)

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
    
    def _send_email(self, user, role):
        template = self.env.ref('project_management.email_template_project_join_notification', raise_if_not_found=False)
        if template:
            context = {
                'sender': self.env.user,
                'recipient': user,
                'role': role,
                'sender_email': self.env.user.email,
                'recipient_email': user.email,
            }
            template.with_context(context).send_mail(self.id, force_send=True)
    
    def _notify_project_members(self, current_ids, new_ids, role):
        """
        Send notifications to added/removed project members
        Args:
            current_ids: set of current member IDs
            new_ids: set of new member IDs
            role: string indicating member role (Developer/QC)
        """
        added_users = new_ids - current_ids
        # removed_users = current_ids - new_ids
        
        # Log changes
        if added_users:
            _logger.info('Added %s: %s', role, list(added_users))
            
        # if removed_users:
        #     _logger.info('Removed %s: %s', role, list(removed_users))
        
        # Send emails to new users
        for user_id in added_users:
            user = self.env['res.users'].browse(user_id)
            # self.message_post(
            #     body=_("Added %s: %s") % (role, user.name),
            #     subtype_id=self.env.ref('mail.mt_note').id
            # )
            _logger.info('Sending email to %s', user.name)
            self._send_email(user, role)

    def _prepare_overview_data(self, project_id):
        """
        Gather overview data for a given project ID.
        """
        project = self.browse(project_id)

        # Project Info
        project_info = {
            'project_code': project.project_code,
            'project_name': project.name,
            'project_manager': project.project_manager.name if project.project_manager else '',
            'start_date': project.start_date,
            'end_date': project.end_date,
            'status': project.state,
        }

        # High-level Progress
        total_tasks = len(project.task_ids)
        status_count = {
            'new': 0,
            'dev': 0,
            'qc': 0,
            'done': 0,
            'cancel': 0,
        }
        for task in project.task_ids:
            status_count[task.state] += 1

        # Team Stats
        dev_stats = {}
        qc_stats = {}
        for task in project.task_ids:
            if task.dev_id:
                dev_name = task.dev_id.name
                dev_stats[dev_name] = dev_stats.get(dev_name, 0) + 1
            if task.qc_id:
                qc_name = task.qc_id.name
                qc_stats[qc_name] = qc_stats.get(qc_name, 0) + 1

        # Sprint Info
        sprint_info = []
        for sprint in project.sprint_ids:
            sprint_data = {
                'sprint_name': sprint.name,
                'sprint_state': sprint.state,
                'start_date': sprint.start_date,
                'end_date': sprint.end_date,
                'tasks_in_sprint': len(sprint.task_ids),
            }
            sprint_info.append(sprint_data)

        # Compile report entry
        overview_entry = {
            'project_info': project_info,
            'progress': {
                'total_tasks': total_tasks,
                'status_count': status_count
            },
            'team_stats': {
                'developer': dev_stats,
                'qc': qc_stats,
            },
            'sprints': sprint_info,
        }
        return overview_entry
    def _convert_overview_to_html(self, overview_data):
        """Convert overview dictionary data to formatted HTML string"""
        
        project_info = overview_data['project_info']
        progress = overview_data['progress'] 
        team_stats = overview_data['team_stats']
        sprints = overview_data['sprints']

        html = f"""
        <div style="font-family: Arial; max-width: 800px; margin: 20px auto;">
            
            <!-- Project Info Section -->
            <div style="border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; background: #f9f9f9;">
                <h2 style="color: #333; margin-top: 0;">{project_info['project_name']} ({project_info['project_code']})</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px;"><strong>Project Manager:</strong></td>
                        <td style="padding: 8px;">{project_info['project_manager']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;"><strong>Start Date:</strong></td>
                        <td style="padding: 8px;">{project_info['start_date']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;"><strong>End Date:</strong></td>
                        <td style="padding: 8px;">{project_info['end_date']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;"><strong>Status:</strong></td>
                        <td style="padding: 8px;">{project_info['status']}</td>
                    </tr>
                </table>
            </div>

            <!-- Progress Section -->
            <div style="border: 1px solid #ddd; padding: 15px; margin-bottom: 20px;">
                <h3 style="color: #333; margin-top: 0;">Progress</h3>
                <p><strong>Total Tasks:</strong> {progress['total_tasks']}</p>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <th style="padding: 8px; text-align: left;">Status</th>
                        <th style="padding: 8px; text-align: left;">Count</th>
                    </tr>
                    {' '.join(f'''
                    <tr>
                        <td style="padding: 8px; border-top: 1px solid #ddd;">{status}</td>
                        <td style="padding: 8px; border-top: 1px solid #ddd;">{count}</td>
                    </tr>
                    ''' for status, count in progress['status_count'].items())}
                </table>
            </div>

            <!-- Team Stats Section -->
            <div style="border: 1px solid #ddd; padding: 15px; margin-bottom: 20px;">
                <h3 style="color: #333; margin-top: 0;">Team Statistics</h3>
                
                <!-- Developer Stats -->
                <div style="margin-bottom: 15px;">
                    <h4 style="color: #666;">Developers</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        {' '.join(f'''
                        <tr>
                            <td style="padding: 8px; border-top: 1px solid #ddd;">{dev_name}</td>
                            <td style="padding: 8px; border-top: 1px solid #ddd;">{task_count} tasks</td>
                        </tr>
                        ''' for dev_name, task_count in team_stats['developer'].items())}
                    </table>
                </div>

                <!-- QC Stats -->
                <div>
                    <h4 style="color: #666;">Quality Control</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        {' '.join(f'''
                        <tr>
                            <td style="padding: 8px; border-top: 1px solid #ddd;">{qc_name}</td>
                            <td style="padding: 8px; border-top: 1px solid #ddd;">{task_count} tasks</td>
                        </tr>
                        ''' for qc_name, task_count in team_stats['qc'].items())}
                    </table>
                </div>
            </div>

            <!-- Sprint Section -->
            <div style="border: 1px solid #ddd; padding: 15px;">
                <h3 style="color: #333; margin-top: 0;">Sprints</h3>
                {''.join(f'''
                <div style="margin-bottom: 10px; padding: 10px; background: #f9f9f9;">
                    <h4 style="margin: 0 0 10px 0;">{sprint['sprint_name']} ({sprint['sprint_state']})</h4>
                    <p style="margin: 5px 0;">Start: {sprint['start_date']}</p>
                    <p style="margin: 5px 0;">End: {sprint['end_date']}</p>
                    <p style="margin: 5px 0;">Tasks: {sprint['tasks_in_sprint']}</p>
                </div>
                ''' for sprint in sprints)}
            </div>
        </div>
        """
        
        return html
    
    def action_send_report_email(self, report, pm, project):
        mitchell_admin = self.env.ref('base.user_admin')
        context = {
            'sender': mitchell_admin.name,
            'sender_mail': mitchell_admin.email,
            'recipient': pm.name,
            'recipient_email': pm.email,
            'project': project.name,
            'body_html': report,
        }
        # _logger.info(context)
        # Gửi email cho PM của project
        template = self.env.ref('project_management.email_template_project_task_report')
        if template:
            template.with_context(context).send_mail(self.id, force_send=True)

    def generate_overview_report(self):
        """
        Generate an overview report with key metrics for each project, 
        then convert each to HTML.
        """
        projects = self.search([])
        for project in projects:
            overview_entry = self._prepare_overview_data(project.id)
            # Chuyển đổi sang HTML cho từng project
            html_overview = self._convert_overview_to_html(overview_entry)
            self.action_send_report_email(html_overview, project.project_manager, project)
            # in ra thông báo cho biết đã gửi thành công
            _logger.info('Email sent to %s', project.project_manager.name)


    def write(self, vals):
        pm_editable_fields = {'description', 'developer_ids', 'qc_ids', 'sprint_ids', 'task_ids'}
        # Handle developer notifications
        if 'developer_ids' in vals:
            current_developer_ids = set(self.developer_ids.ids)
            new_developer_ids = set(vals['developer_ids'][0][2])
            self._notify_project_members(current_developer_ids, new_developer_ids, 'Developer')
        
        # Handle QC notifications
        if 'qc_ids' in vals:
            current_qc_ids = set(self.qc_ids.ids)
            new_qc_ids = set(vals['qc_ids'][0][2])
            self._notify_project_members(current_qc_ids, new_qc_ids, 'Quality Control')
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