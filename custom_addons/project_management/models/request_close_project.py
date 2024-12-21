from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RequestCloseProject(models.Model):
    _name = 'request.close.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Request Close Project'

    code = fields.Char(string='Requets Close Project Code',
                       required=True,
                       readonly=True,
                       default=_('New'))
    name = fields.Char(string='Request Close Project Name')
    project_id = fields.Many2one('project.management',
                                    string='Project',
                                    required=True)
    # trạng thái (nhaps gửi duyệt duyệt hủy)
    state = fields.Selection([
                                ('draft', 'Draft'),
                                ('submited', 'Submited'),
                                ('approved', 'Approved'),
                                ('canceled', 'Canceled')
                            ], string='Status', 
                            tracking=True, 
                            default='draft')
    # lý do hủy yêu cầu
    reason_cancel = fields.Text(string='Reason Cancel')
    # lý do hủy dự án
    reason_close = fields.Text(string='Reason Close', 
                               required=True)
    

    def action_approve_request(self):
        for record in self:
            if record.state != 'submited':
                raise ValidationError("Only submited records can be approved.")
            if record.project_id.start_date > fields.Date.today():
                raise ValidationError("Project has not started yet.")
            
            record.state = 'approved'
            record.project_id.state = 'close'
            record.project_id.end_date = fields.Date.today()
            
            # Send email notification
            template = self.env.ref('project_management.email_template_request_close_approved')
            if template:
                template.send_mail(record.id, force_send=True)

    # thêm một hàm để set state của các bản ghi được đưa vào hàm thành "approve"
    @api.model
    def approve_request(self, record_ids):
        records = self.browse(record_ids)
        
        # Check if all records are in 'submited' state
        invalid_records = records.filtered(lambda r: r.state != 'submited')
        if invalid_records:
            invalid_names = ', '.join(invalid_records.mapped('project_id.name'))
            return {
                'status': 'error',
                'message': f'These records must be in submitted state: {invalid_names}'
            }

        # Check all projects' sprints and tasks
        for record in records:
            project = record.project_id
            incomplete_sprints = project.sprint_ids.search([('state', '!=', 'close'),('project_id', '=', project.id)]).mapped('name')
            incomplete_tasks = project.task_ids.search([('state', '!=', 'done'), ('project_id', '=', project.id)]).mapped('name')
            
            if incomplete_sprints or incomplete_tasks:
                details = []
                if incomplete_sprints:
                    details.append(f"Sprints: {', '.join(incomplete_sprints)}")
                if incomplete_tasks:
                    details.append(f"Tasks: {', '.join(incomplete_tasks)}")
                return {
                    'status': 'error',
                    'message': f'Project {project.name} has incomplete items: {"; ".join(details)}'
                }

        records.write({'state': 'approved'})
        approved_names = ', '.join(records.mapped('project_id.name'))
        return {
            'status': 'success',
            'message': f'Selected records have been approved: {approved_names}'
        }
    
    @api.model
    def cancel_request(self, record_ids):
        records = self.browse(record_ids)
        invalid_records = records.filtered(lambda r: r.state != 'submited')
        if invalid_records:
            invalid_names = ', '.join(invalid_records.mapped('project_id.name'))
            return {
                'status': 'error',
                'message': f'Only submited records can be canceled: {invalid_names}'
            }
        
        records.write({'state': 'canceled'})
        canceled_names = ', '.join(records.mapped('project_id.name'))
        return {
            'status': 'success',
            'message': f'Selected records have been canceled: {canceled_names}'
        }

    def write(self, vals):
        res = super(RequestCloseProject, self).write(vals)
        if 'state' in vals and vals['state'] == 'approved':
            for record in self:
                record.project_id.write({'state': 'close'})
        return res

    # ghi đè phương thức create để tạo mã tự động    
    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('request.close.project') or 'New'
        return super(RequestCloseProject, self).create(vals)
