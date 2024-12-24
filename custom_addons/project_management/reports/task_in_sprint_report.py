from odoo import models, fields, api, tools

class ProjectTaskReport(models.Model):
    _name = 'project.tasks.report'
    _description = 'Project Task Report'
    _auto = False

    member_id = fields.Many2one('res.users', string='Member')
    project_manager = fields.Many2one('res.users', string='Project Manager')
    project_id = fields.Many2one('project.management', string='Project')
    sprint_id = fields.Many2one('project.sprint', string='Sprint')
    role = fields.Selection([
        ('dev', 'Developer'),
        ('qc', 'Quality Control'),
        ('project_manager', 'Project Manager')
    ], string='Role')
    task_id = fields.Many2one('project.tasks', string='Task')
    task_name = fields.Char(string='Task Name')
    task_state = fields.Selection([
        ('new', 'New'),
        ('dev', 'Developer is working'),
        ('qc', 'Quality Control is working'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Task State')
    total_tasks = fields.Integer(string='Total Tasks')
    new_tasks = fields.Integer(string='New Tasks')
    dev_tasks = fields.Integer(string='Dev Tasks')
    qc_tasks = fields.Integer(string='QC Tasks')
    done_tasks = fields.Integer(string='Done Tasks')

    @api.model
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'project_tasks_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW project_tasks_report AS (
                SELECT
                    t.id * 10 + 1 AS id,  -- Unique ID for dev
                    t.dev_id AS member_id,
                    pm.project_manager AS project_manager,
                    t.project_id AS project_id,
                    t.sprint_id AS sprint_id,
                    'dev' AS role,
                    t.id AS task_id,
                    t.name AS task_name,
                    t.state AS task_state,
                    COUNT(t.id) OVER (PARTITION BY t.project_id) AS total_tasks,
                    SUM(CASE WHEN t.state = 'new' THEN 1 ELSE 0 END) AS new_tasks,
                    SUM(CASE WHEN t.state = 'dev' THEN 1 ELSE 0 END) AS dev_tasks,
                    SUM(CASE WHEN t.state = 'qc' THEN 1 ELSE 0 END) AS qc_tasks,
                    SUM(CASE WHEN t.state = 'done' THEN 1 ELSE 0 END) AS done_tasks
                FROM
                    project_tasks t
                    JOIN res_users u ON t.dev_id = u.id
                    JOIN project_management pm ON t.project_id = pm.id
                GROUP BY
                    t.id, t.dev_id, pm.project_manager, t.project_id, t.sprint_id, t.name, t.state
                UNION ALL
                SELECT
                    t.id * 10 + 2 AS id,  -- Unique ID for qc
                    t.qc_id AS member_id,
                    pm.project_manager AS project_manager,
                    t.project_id AS project_id,
                    t.sprint_id AS sprint_id,
                    'qc' AS role,
                    t.id AS task_id,
                    t.name AS task_name,
                    t.state AS task_state,
                    COUNT(t.id) OVER (PARTITION BY t.project_id) AS total_tasks,
                    SUM(CASE WHEN t.state = 'new' THEN 1 ELSE 0 END) AS new_tasks,
                    SUM(CASE WHEN t.state = 'dev' THEN 1 ELSE 0 END) AS dev_tasks,
                    SUM(CASE WHEN t.state = 'qc' THEN 1 ELSE 0 END) AS qc_tasks,
                    SUM(CASE WHEN t.state = 'done' THEN 1 ELSE 0 END) AS done_tasks
                FROM
                    project_tasks t
                    JOIN res_users u ON t.qc_id = u.id
                    JOIN project_management pm ON t.project_id = pm.id
                GROUP BY
                    t.id, t.qc_id, pm.project_manager, t.project_id, t.sprint_id, t.name, t.state
            )
        """)

    @api.model
    def show_project_tasks(self, record_ids):
        records = self.sudo().search([('project_manager', '=', 10)])
        for record in records:
            print(record.task_name)
        project_task_report = self.browse(record_ids[0])
        print('Project Task Report', project_task_report)
        project_id = project_task_report.project_id.id
        print('Project Name', project_task_report.project_id.name)

        # Lấy action bằng ID và ghi đè thuộc tính
        action = self.with_context(active_id=project_id, active_ids=[project_id]) \
            .env.ref('project_management.action_project_task_list') \
            .sudo().read()[0]

        # Cập nhật context và domain của action
        action['context'] = {'default_project_id': project_id}
        action['domain'] = [('project_id', '=', project_id)]
        action['target'] = 'new'  # Mở action dưới dạng pop-up
        action['display_name'] = f'Tasks of Project {project_task_report.project_id.name}'
        print(action)

        return action
    
    @api.model
    def show_new_project_tasks(self, record_ids):
        project_task_report = self.browse(record_ids[0])
        print('Project Task Report', project_task_report)
        project_id = project_task_report.project_id.id
        print('Project Name', project_task_report.project_id.name)

        # Lấy action bằng ID và ghi đè thuộc tính
        action = self.with_context(active_id=project_id, active_ids=[project_id]) \
            .env.ref('project_management.action_project_task_list') \
            .sudo().read()[0]
        print(action)

        # Cập nhật context và domain của action để chỉ hiển thị các task mới
        action['context'] = {'default_project_id': project_id}
        action['domain'] = [('project_id', '=', project_id), ('state', '=', 'new')]
        action['target'] = 'new'  # Mở action dưới dạng pop-up
        action['display_name'] = f'New Tasks of Project {project_task_report.project_id.name}'
        print(action)

        return action
    
    @api.model
    def show_dev_project_tasks(self, record_ids):
        project_task_report = self.browse(record_ids[0])
        print('Project Task Report', project_task_report)
        project_id = project_task_report.project_id.id
        print('Project Name', project_task_report.project_id.name)

        # Lấy action bằng ID và ghi đè thuộc tính
        action = self.with_context(active_id=project_id, active_ids=[project_id]) \
            .env.ref('project_management.action_project_task_list') \
            .sudo().read()[0]
        # print(action)

        # Cập nhật context và domain của action để chỉ hiển thị các task đang được phát triển
        action['context'] = {'default_project_id': project_id}
        action['domain'] = [('project_id', '=', project_id), ('state', '=', 'dev')]
        action['target'] = 'new'  # Mở action dưới dạng pop-up
        action['display_name'] = f'Development Tasks of Project {project_task_report.project_id.name}'
        print(action)

        return action
    
    @api.model
    def show_qc_project_tasks(self, record_ids):
        project_task_report = self.browse(record_ids[0])
        print('Project Task Report', project_task_report)
        project_id = project_task_report.project_id.id
        print('Project Name', project_task_report.project_id.name)

        # Lấy action bằng ID và ghi đè thuộc tính
        action = self.with_context(active_id=project_id, active_ids=[project_id]) \
            .env.ref('project_management.action_project_task_list') \
            .sudo().read()[0]
        # print(action)

        # Cập nhật context và domain của action để chỉ hiển thị các task đang được phát triển
        action['context'] = {'default_project_id': project_id}
        action['domain'] = [('project_id', '=', project_id), ('state', '=', 'qc')]
        action['target'] = 'new'  # Mở action dưới dạng pop-up
        action['display_name'] = f'Quality Control Tasks of Project {project_task_report.project_id.name}'
        print(action)

        return action
    
    @api.model
    def show_done_project_tasks(self, record_ids):
        project_task_report = self.browse(record_ids[0])
        print('Project Task Report', project_task_report)
        project_id = project_task_report.project_id.id
        print('Project Name', project_task_report.project_id.name)

        # Lấy action bằng ID và ghi đè thuộc tính
        action = self.with_context(active_id=project_id, active_ids=[project_id]) \
            .env.ref('project_management.action_project_task_list') \
            .sudo().read()[0]
        # print(action)

        # Cập nhật context và domain của action để chỉ hiển thị các task đang được phát triển
        action['context'] = {'default_project_id': project_id}
        action['domain'] = [('project_id', '=', project_id), ('state', '=', 'done')]
        action['target'] = 'new'  # Mở action dưới dạng pop-up
        action['display_name'] = f'Quality Control Tasks of Project {project_task_report.project_id.name}'
        print(action)

        return action