from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RequestOpenProject(models.Model):
    _name = 'request.open.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Request Open Project'

    # thêm một field để lưu mã yêu cầu mở dự án
    code = fields.Char(string='Code Request Open Project', 
                       required=True, 
                       copy=False, 
                       readonly=True, 
                       index=True, 
                       default=_('New'))
    # thêm field để lưu tên dự án
    name = fields.Char(string='Project Name', 
                       required=True)
    # thêm field để lưu thông ti PM
    project_manager = fields.Many2one('res.users', 
                                      string='Project Manager', 
                                      required=True)
    # thêm field để lưu thông tin về dev, một dự án có nhiều devdev
    developer_ids = fields.Many2many('res.users', 
                                        'request_project_developer_rel',  # Intermediate table name
                                        'project_id',  # Column in the intermediate table for the current model
                                        'user_id',  # Column in the intermediate table for the related model
                                        string='Developer', 
                                        required=True)
    # thêm field để lưu thông tin về qc
    qc_ids = fields.Many2many('res.users', 
                            'request_project_qc_rel',  # Intermediate table name
                            'project_id',  # Column in the intermediate table for the current model
                            'user_id',  # Column in the intermediate table for the related model
                            string='QC', 
                            required=True)
    # thêm field để lưu thông tin về ngày bắt đầu của dự án
    start_date = fields.Date(string='Start Date', 
                             required=True)
    # ?thêm field để nhập mô tả của dự án
    description = fields.Text(string='Description')
    # thêm field để lưu trạng thái của yêu cầu
    # có 4 trạng thái là nháp gửi duyệt đã duyệt hủy
    state = fields.Selection([
                                ('draft', 'Draft'),
                                ('submited', 'Submited'),
                                ('approved', 'Approved'),
                                ('canceled', 'Canceled'),
                            ], 
                            string='Status',  
                            copy=False, 
                            tracking=True,
                            default='draft')
    # lý do hủy yêu cầu
    cancel_reason = fields.Text(string='Cancel Reason')

   # thêm một hàm để set state của các bản ghi được đưa vào hàm thành "approve"
    @api.model
    def approve_request(self, record_ids):
        records = self.browse(record_ids)
        invalid_records = records.filtered(lambda r: r.state != 'submited')
        if invalid_records:
            return {
                'status': 'error',
                'message': 'Only submited records can be approved. Invalid records: %s' % ', '.join(invalid_records.mapped('name')),
            }
        records.write({'state': 'approved'})
        return {
            'status': 'success',
            'message': 'Selected records have been approved. Approved records: %s' % ', '.join(records.mapped('name')),
        }
    
    @api.model
    def cancel_request(self, record_ids):
        records = self.browse(record_ids)
        invalid_records = records.filtered(lambda r: r.state != 'submited')
        if invalid_records:
            return {
                'status': 'error',
                'message': 'Only submited records can be canceled. Invalid records: %s' % ', '.join(invalid_records.mapped('name')),
            }
        
        # Kiểm tra trường 'cancel_reason'
        missing_reason_records = records.filtered(lambda r: not r.cancel_reason)
        if missing_reason_records:
            return {
                'status': 'error',
                'message': 'The following records are missing a cancellation reason: %s' % ', '.join(missing_reason_records.mapped('name')),
            }
    
        records.write({'state': 'canceled'})
        return {
            'status': 'success',
            'message': 'Selected records have been canceled. Canceled records: %s' % ', '.join(records.mapped('name')),
        }
    
    def send_project_creation_email(self, record, templates_id):
        template = self.env.ref(templates_id)
        template.send_mail(record.id, force_send=True) 

    # ghi đè phương thức create để tạo mà tự động dựa vào sequence
    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('request.open.project') or _('New')
        return super(RequestOpenProject, self).create(vals)
    # ghi đè phương thức write để tạo project mới khi state chuyển thành approved
    def write(self, vals):
        res = super(RequestOpenProject, self).write(vals)
        if 'state' in vals and vals['state'] == 'approved':
            for record in self:
                self.env['project.management'].create({
                    'name': record.name,
                    'project_manager': record.project_manager.id,
                    'developer_ids': [(6, 0, record.developer_ids.ids)],
                    'qc_ids': [(6, 0, record.qc_ids.ids)],
                    'start_date': record.start_date,
                    'description': record.description,
                })
                self.send_project_creation_email(record, 'project_management.email_template_project_open_approved')
        if 'state' in vals and vals['state'] == 'canceled':
            for record in self:
                self.send_project_creation_email(record, 'project_management.email_template_project_open_canceled')
        return res