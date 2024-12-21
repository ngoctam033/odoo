from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
import logging
_logger = logging.getLogger(__name__)

class Task(models.Model):
    _name = 'project.tasks'
    _description = 'Project Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'task_code desc'

    task_code = fields.Char(string='Task Code', 
                            readonly=True, 
                            default='New')
    name = fields.Char(string='Task Name', 
                       required=True)
    project_id = fields.Many2one('project.management', 
                                 string='Project', 
                                 required=True, 
                                 ondelete='cascade')
    sprint_id = fields.Many2one('project.sprint', 
                                string='Sprint', 
                                ondelete='set null')
    dev_id = fields.Many2one('res.users', 
                             string='Developer',
                             required=True,
                             ondelete='restrict',
                             tracking=True)
    qc_id = fields.Many2one('res.users', 
                            string='Quality Control',
                            required=True,
                            ondelete='restrict',
                            tracking=True)
    task_type = fields.Many2one('project.tasks.type', 
                                string='Task Type', 
                                required=True)
    dev_deadline = fields.Date(string='Developer Deadline',
                               tracking=True)
    qc_deadline = fields.Date(string='Quality Control Deadline',
                              tracking=True)
    state = fields.Selection([
        ('new', 'New'),
        ('dev', 'Developer is working'),
        ('qc', 'Quality Control is working'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='new', tracking=True)
    description = fields.Text(string='Description')
    return_reason = fields.Text(string='Return Reason')
    
    def action_dev_working(self):
        for rec in self:
            if rec.state != 'new':
                raise UserError("Chỉ các task ở trạng thái 'New' mới có thể chuyển sang 'Dev'.")
            if not self.env.user.has_group('project_management.group_project_manager') and \
               self.env.user != rec.dev_id:
                raise AccessError("Bạn không được phép bắt đầu phát triển task này.")
            rec.state = 'dev'

    def action_submit_qc(self):
        for rec in self:
            if rec.state != 'dev':
                raise UserError("Chỉ các task ở trạng thái 'Dev' mới có thể chuyển sang 'QC'.")
            if not self.env.user.has_group('project_management.group_project_manager') and \
               self.env.user != rec.dev_id:
                raise AccessError("Bạn không được phép gửi task này đến QC.")
            rec.state = 'qc'
            
            # Send email to QC notifying task completion
            template = self.env.ref('project_management.email_template_task_completed')
            if template:
                template.send_mail(rec.id, force_send=True)

    def action_set_done(self):
        for rec in self:
            if rec.state != 'qc':
                raise UserError("Chỉ các task ở trạng thái 'QC' mới có thể được đặt là 'Done'.")
            if not self.env.user.has_group('project_management.group_project_manager') and \
               self.env.user != rec.qc_id:
                raise AccessError("Bạn không được phép đặt task này là Done.")
            rec.state = 'done'
            _logger.info('Task "%s" đã được đặt là Done bởi %s.', rec.name, self.env.user.name)
                        
            # Send email to PM
            template = self.env.ref('project_management.email_template_task_done')
            if template:
                template.send_mail(rec.id, force_send=True)

    def action_return_to_dev(self):
        for rec in self:
            if rec.state != 'qc':
                raise UserError("Chỉ các task ở trạng thái 'QC' mới có thể được chuyển về 'Dev'.")
            if not self.env.user.has_group('project_management.group_project_manager') and \
               self.env.user != rec.qc_id:
                raise AccessError("Bạn không được phép chuyển task này về Dev.")
            rec.state = 'dev'
            _logger.info('Task "%s" đã được chuyển về Dev bởi %s.', rec.name, self.env.user.name)

            # Send email to Developer
            template = self.env.ref('project_management.email_template_task_returned')
            if template:
                template.send_mail(rec.id, force_send=True)

    @api.model
    def update_tasks(self, new_sprint_id, project_id):
        try:
            tasks = self.search([('state', '!=', 'done'), 
                                 ('project_id', '=', project_id), 
                                 ('sprint_id', '!=', new_sprint_id)])
            if not tasks:
                return {'status': 'warning', 'message': 'Không có task nào cần cập nhật.'}

            new_sprint = self.env['project.sprint'].browse(new_sprint_id)
            if not new_sprint:
                return {'status': 'error', 'message': 'Sprint mới không tồn tại.'}

            for task in tasks:
                task.sprint_id = new_sprint.id

            return {'status': 'success', 'message': 'Đã đẩy thành công các task sang sprint mới.'}
        except Exception as e:
            # Log the exception
            _logger.error("Error updating tasks: %s", e)
            # Raise a user-friendly error
            raise UserError("An error occurred while updating tasks. Please try again later.")
        
    @api.model
    def create(self, vals):
        if vals.get('task_code', 'New') == 'New':
            vals['task_code'] = self.env['ir.sequence'].next_by_code('project.tasks') or 'New'
        return super(Task, self).create(vals)