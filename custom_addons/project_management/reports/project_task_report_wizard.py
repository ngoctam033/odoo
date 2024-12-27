from odoo import models, fields, api
from odoo.exceptions import ValidationError
import xlsxwriter
import base64
import datetime
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)


class ProjectTaskReportWizard(models.TransientModel):
    _name = 'project.task.report.wizard'
    _description = 'Project Task Report Wizard'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    project_ids = fields.Many2many('project.management', string='Projects')

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise ValidationError("'Date From' must be less than or equal to 'Date To'")

    def _get_projects(self):
        if not self.project_ids:
            return self.env['project.management'].search([])
        return self.project_ids

    def _create_excel_file(self, sheet_name, headers, data):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet(sheet_name)

        # Add formats
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})

        # Write headers
        column_widths = [len(header) for header in headers]
        for col, header_text in enumerate(headers):
            sheet.write(0, col, header_text, header_format)
            column_widths[col] = max(column_widths[col], len(header_text))

        # Write data
        for row, row_data in enumerate(data, start=1):
            for col, cell_data in enumerate(row_data):
                if isinstance(cell_data, datetime.date):
                    sheet.write(row, col, cell_data, date_format)
                    cell_length = len(cell_data.strftime('%d/%m/%Y'))
                else:
                    sheet.write(row, col, cell_data)
                    cell_length = len(str(cell_data))
                column_widths[col] = max(column_widths[col], cell_length)

        # Set column widths
        for col, width in enumerate(column_widths):
            sheet.set_column(col, col, width)

        workbook.close()
        return output.getvalue()

    def _create_attachment(self, file_name, file_data):
        return self.env['ir.attachment'].create({
            'name': file_name,
            'type': 'binary',
            'datas': base64.b64encode(file_data)
        })

    def action_open_report(self):
        self.ensure_one()
        domain = []
        
        if self.project_ids:
            domain.append(('project_id', 'in', self.project_ids.ids))
        
        if self.date_from:
            domain.append(('task_id.create_date', '>=', self.date_from))
        
        if self.date_to:
            domain.append(('task_id.create_date', '<=', self.date_to))
        
        return {
            'name': 'Project Task Report',
            'type': 'ir.actions.act_window',
            'res_model': 'project.tasks.report',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'search_default_group_by_project': 1},
        }

    def action_export_report(self):
        self.ensure_one()
        projects = self._get_projects()

        # Create domain to filter tasks
        domain = [
            ('project_id', 'in', projects.ids),
            '|',
            ('dev_deadline', '>=', (datetime.datetime.combine(fields.Date.context_today(self) + datetime.timedelta(days=2), datetime.time(0,0,0)).isoformat())),
            ('qc_deadline', '>=', (datetime.datetime.combine(fields.Date.context_today(self) + datetime.timedelta(days=2), datetime.time(0,0,0)).isoformat()))
        ]
        
        # Get tasks based on domain
        tasks = self.env['project.tasks'].search(domain)
        
        # Prepare data for Excel
        headers = ['Task Code', 'Name', 'Project', 'Developer', 'QC', 'Dev Deadline', 'QC Deadline', 'State']
        data = [
            [
                task.task_code,
                task.name,
                task.project_id.name,
                task.dev_id.name,
                task.qc_id.name,
                task.dev_deadline,
                task.qc_deadline,
                task.state
            ]
            for task in tasks
        ]

        # Create Excel file
        xlsx_data = self._create_excel_file('Project Task Report', headers, data)
        
        # Create attachment
        attachment = self._create_attachment('Project_Task_Report.xlsx', xlsx_data)

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_export_task_in_sprint_report(self):
        self.ensure_one()
        projects = self._get_projects()

        # Create domain to filter tasks in sprint
        domain = [
            ('project_id', 'in', projects.ids)
        ]
        
        # Get tasks in sprint based on domain
        tasks = self.env['project.tasks.report'].search(domain)
        
        # Prepare data for Excel
        headers = ['Member', 'Project Manager', 'Project', 'Sprint', 'Role', 'Task ID', 'Task Name', 'Task State', 'Total Tasks', 'New Tasks', 'Dev Tasks', 'QC Tasks', 'Done Tasks']
        data = [
            [
                task.member_id.name,
                task.project_manager.name,
                task.project_id.name,
                task.sprint_id.name,
                task.role,
                task.task_id.name,
                task.task_state,
                task.total_tasks,
                task.new_tasks,
                task.dev_tasks,
                task.qc_tasks,
                task.done_tasks
            ]
            for task in tasks
        ]

        # Create Excel file
        xlsx_data = self._create_excel_file('Task In Sprint Report', headers, data)
        
        # Create attachment
        attachment = self._create_attachment('Task_In_Sprint_Report.xlsx', xlsx_data)

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
    
    def action_send_report_email(self):
        projects = self._get_projects()

        for project in projects:
            pm = project.project_manager
            if not pm:
                continue  # Bỏ qua nếu project không có PM

            # Lấy thống kê task cho project hiện tại
            # stats = self._get_task_statistics_for_project(project)
            html_report = "<div><h1>Project Task Report</h1></div>"
            mitchell_admin = self.env.ref('base.user_admin')
            context = {
                'sender': mitchell_admin.name,
                'sender_mail': mitchell_admin.email,
                'recipient': pm.name,
                'recipient_email': pm.email,
                'project': project.name,
                'body_html': html_report,
            }
            _logger.info(context)
            # Gửi email cho PM của project
            template = self.env.ref('project_management.email_template_project_task_report')
            if template:
                template.with_context(context).send_mail(self.id, force_send=True)

