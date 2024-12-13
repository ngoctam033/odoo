from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RequestOpenProject(models.Model):
    _name = 'project.management.request.open.project'
    _description = 'Request Open Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    request_code = fields.Char(string='Request Code', 
                               readonly=True)
    project_name = fields.Char(string='Project Name', 
                               required=True)
    pm_id = fields.Many2one('res.users', 
                            string='Project Manager', 
                            required=True)
    developer_ids = fields.Many2many('res.users', 
                                     'request_open_project_developer_rel', 
                                     string='Developer', 
                                     tracking=True)
    qc_ids = fields.Many2many('res.users', 
                              'request_open_project_qc_rel', 
                              string='Quality Control', 
                              tracking=True)
    start_date = fields.Date(string='Start Date', 
                             required=True)
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    cancel_reason = fields.Text(string='Cancel Reason')

    @api.model
    def create(self, vals):
        if vals.get('request_code', 'New') == 'New':
            vals['request_code'] = self.env['ir.sequence'].next_by_code('request.open.project') or 'New'
        return super(RequestOpenProject, self).create(vals)

    @api.model
    def default_get(self, fields):
        res = super(RequestOpenProject, self).default_get(fields)
        if 'request_code' in fields:
            res['request_code'] = self.env['ir.sequence'].next_by_code('request.open.project') or 'New'
        return res