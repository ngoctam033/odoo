from . import models
from . import controllers
from . import wizards
from . import reports

from odoo import fields
from datetime import timedelta
import random

from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def generate_demo_data(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Lấy tham chiếu đến nhóm Project/Admin
    group_project_admin = env.ref('project_management.group_project_admin')
    group_project_pm = env.ref('project_management.group_project_pm')
    group_project_member = env.ref('project_management.group_project_member')

    # Tạo các bản ghi mẫu cho user admin
    with env.cr.savepoint():
        User = env['res.users'].with_context({'no_reset_password': True}).sudo()
        login = f'admin_user_2'
        # tạo useruser
        if not User.search([('login', '=', login)], limit=1):
            # tạo useruser
            for i in range(1, 3):
                user = User.create({
                    'name': f'Admin User {i}',
                    'login': f'admin_user_{i}',
                    'share': False,
                    'email': f'admin_user_{i}@demo.com',
                    'groups_id': [(6, 0, [group_project_admin.id, 1])],
                    'password': 'demo',
                    'role': 'project_manager'
                })
                _logger.info('Created user: %s with Project/Admin rights', user.name)

            for i in range(1, 11):
                user = User.create({
                    'name': f'Project Manager {i}',
                    'login': f'project_manager_{i}',
                    'share': False,
                    'email': f'project_manager_{i}@demo.com',
                    'groups_id': [(6, 0, [group_project_pm.id, 1])],
                    'password': 'demo',
                    'role': 'project_manager'
                })
                _logger.info('Created user: %s with Project/Admin rights', user.name)

            for i in range(1, 21):
                user = User.create({
                    'name': f'Quality Control {i}',
                    'login': f'qc_{i}',
                    'share': False,
                    'email':f'qc_user_{i}@demo.com',
                    'groups_id': [(6, 0, [group_project_member.id, 1])],
                    'password': 'demo',
                    'role': 'qc'
                })
                _logger.info('Created user: %s with Quality Control rights', user.name)

            for i in range(21,81):
                user = User.create({
                    'name': f'Developer {i}',
                    'login': f'developer_{i}',
                    'share': False,
                    'email':f'developer_user_{i}@demo.com',
                    'groups_id': [(6, 0, [group_project_member.id, 1])],
                    'password': 'demo',
                    'role': 'developer'
                })
                _logger.info('Created user: %s with Developer rights', user.name)
        else:
            _logger.info('Users already exist, skipping creation')
       
       # Tạo dữ liệu mẫu cho Project Management
        Project = env['project.management'].sudo()
        for i in range(1, 6):
            project = Project.create({
                'name': f'Project {i}',
                'start_date': fields.Date.today() + timedelta(days=random.randint(1, 15)) - timedelta(days=random.randint(1, 30)),
                'end_date': fields.Date.today() + timedelta(days=random.randint(31, 100)),
                'project_manager': random.choice(User.search(['|', ('login', 'like', 'project_manager_%'), ('login', 'like', 'admin_user_%')]).ids),
                'developer_ids': [(6, 0, User.search([('login', 'like', 'developer_')], limit=random.randint(2, 10)).ids)],
                'qc_ids': [(6, 0, User.search([('login', 'like', 'qc_')], limit=random.randint(1, 5)).ids)],
                'description': f'Description for Project {i}',
            })
            _logger.info('Created project: %s', project.name)
        
        # Tạo dữ liệu mẫu cho Task Type
        TaskType = env['project.tasks.type'].sudo()
        task_types = []
        for i in range(1, 6):
            task_type = TaskType.create({
                'name': f'Task Type {i}',
            })
            task_types.append(task_type.id)
            _logger.info('Created task type: %s', task_type.name)
        
        # Tạo dữ liệu mẫu cho Sprint
        Sprint = env['project.sprint'].sudo()
        Task = env['project.tasks'].sudo()
        projects = Project.search([])
        for project in projects:
            project_duration = (project.end_date - project.start_date).days
            sprint_duration = project_duration // 3
            for j in range(3):
                sprint_start_date = project.start_date + timedelta(days=j * sprint_duration)
                sprint_end_date = sprint_start_date + timedelta(days=sprint_duration - 1)
                sprint = Sprint.create({
                    'name': f'Sprint {j + 1} for Project {project.id}',
                    'start_date': sprint_start_date,
                    'end_date': sprint_end_date,
                    'project_id': project.id,
                })
                # Tạo task cho sprint đầu tiên của mỗi project
                if j == 0:
                    for k in range(1, 6):  # Tạo 5 task cho mỗi sprint đầu tiên
                        task = Task.create({
                            'name': f'Task {k} for Sprint {j + 1} of Project {project.id}',
                            'sprint_id': sprint.id,
                            'project_id': project.id,
                            'task_type': random.choice(task_types),
                            'dev_id': random.choice(project.developer_ids.ids),
                            'qc_id': random.choice(project.qc_ids.ids),
                            'dev_deadline': sprint.start_date + timedelta(days=random.randint(1, 2)),
                            'qc_deadline': sprint.start_date + timedelta(days=random.randint(3, 5)),
                            'description': f'Description for Task {k} of Sprint {j + 1} of Project {project.id}',
                        })
                        _logger.info('Created task: %s', task.name)
                _logger.info('Created sprint: %s', sprint.name)

            # Tạo dữ liệu mẫu cho Request Open Project
        
        # tạo dữ liệu mẫu cho request_open_projectproject
        RequestOpenProject = env['request.open.project'].sudo()
        for i in range(1, 6):
            request_open_project = RequestOpenProject.create({
                'name': f'Request Open Project {i}',
                'project_manager': random.choice(User.search(['|', ('login', 'like', 'project_manager_%'), ('login', 'like', 'admin_user_%')]).ids),
                'developer_ids': [(6, 0, User.search([('login', 'like', 'developer_%')], limit=random.randint(2, 5)).ids)],
                'qc_ids': [(6, 0, User.search([('login', 'like', 'qc_%')], limit=random.randint(1, 3)).ids)],
                'start_date': fields.Date.today() + timedelta(days=random.randint(1, 30)),
                'description': f'Description for Request Open Project {i}',
            })
            _logger.info('Created request open project: %s', request_open_project.name)
        
        # Tạo dữ liệu mẫu cho request close project
        RequestCloseProject = env['request.close.project'].sudo()
        for i in range(1, 6):
            request_close_project = RequestCloseProject.create({
                'name': f'Request Close Project {i}',
                'project_id': random.choice(projects.ids),
                'reason_close': f'Reason Close for Request Close Project {i}',
            })
            _logger.info('Created request close project: %s', request_close_project.name)