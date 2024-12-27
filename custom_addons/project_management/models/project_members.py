from odoo import models, fields, api, _

class ProjectMember(models.Model):
    _inherit = 'res.users'
    _description = 'Project Member'
    
    role = fields.Selection([
        ('project_manager', 'Project Manager'),
        ('developer', 'Developer'),
        ('qc', 'Quality Control'),
    ], string='Role')