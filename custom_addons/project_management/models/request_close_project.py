from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RequestCloseProject(models.Model):
    _name = 'request.close.project'
    _description = 'Request Close Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    request_code = fields.Char(string='Request Code', readonly=True, default='New')
    project_id = fields.Many2one('project.management', string='Project', required=True, ondelete='cascade')
    pm_id = fields.Many2one('res.users', string='Project Manager', required=True)
    end_date = fields.Date(string='End Date', required=True)
    close_reason = fields.Text(string='Close Reason', required=True)
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
            vals['request_code'] = self.env['ir.sequence'].next_by_code('request.close.project') or 'New'
        return super(RequestCloseProject, self).create(vals)

    @api.model
    def default_get(self, fields):
        res = super(RequestCloseProject, self).default_get(fields)
        if 'request_code' in fields:
            res['request_code'] = self.env['ir.sequence'].next_by_code('request.close.project') or 'New'
        return res