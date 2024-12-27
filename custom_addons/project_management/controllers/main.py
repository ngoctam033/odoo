from odoo import http
from odoo.http import request
import json

class ProjectManagementController(http.Controller):

    @http.route('/api/projects', type='http', auth='user', methods=['GET'], csrf=False)
    def get_projects(self, **kwargs):
        # Lấy domain từ query parameters
        domain = []
        if 'project_manager' in kwargs:
            # Tìm kiếm người dùng theo login
            pm_user = request.env['res.users'].search([('login', '=', kwargs['project_manager'])], limit=1)
            if pm_user:
                domain.append(('project_manager', '=', pm_user.id))
            else:
                return request.make_response(json.dumps({'error': 'Project Manager not found'}), headers={'Content-Type': 'application/json'}, status=404)
        if 'state' in kwargs:
            domain.append(('state', '=', kwargs['state']))
        if 'start_date' in kwargs:
            domain.append(('start_date', '>=', kwargs['start_date']))
        if 'end_date' in kwargs:
            domain.append(('end_date', '<=', kwargs['end_date']))

        # Lấy danh sách dự án theo domain và quyền của người dùng
        projects = request.env['project.management'].search(domain)
        
        # Kiểm tra nếu không có dự án nào được tìm thấy
        if not projects:
            return request.make_response(json.dumps({'message': 'No projects found'}), headers={'Content-Type': 'application/json'}, status=404)

        # Chuẩn bị dữ liệu để trả về
        project_data = []
        for project in projects:
            project_data.append({
                'id': project.id,
                'project_code': project.project_code,
                'name': project.name,
                'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
                'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
                'state': project.state,
                'project_manager': project.project_manager.name if project.project_manager else None,
                'developer_ids': [dev.name for dev in project.developer_ids],
                'qc_ids': [qc.name for qc in project.qc_ids],
                'description': project.description,
                'sprint_ids': [{'id': sprint.id, 'name': sprint.name} for sprint in project.sprint_ids],
                'task_ids': [{'id': task.id, 'name': task.name} for task in project.task_ids],
                'task_count': project.task_count,
            })

        return request.make_response(json.dumps(project_data), headers={'Content-Type': 'application/json'})
    