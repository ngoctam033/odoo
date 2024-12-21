from odoo import http
from odoo.http import request

class ProjectManagementController(http.Controller):

    @http.route('/project_management/update_sprint', type='json', auth='user')
    def update_sprint(self):
        return {'status': 'success'}