import time
import json
import datetime
import io
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class ExcelWizard(models.TransientModel):
    _name = "estate.report.wizard"
    _description = "Estate Report Wizard"

    start_date = fields.Date(string="Start Date", default=fields.Date.context_today, required=True)
    end_date = fields.Date(string="End Date", default=fields.Date.context_today, required=True)
    buyer_ids = fields.Many2many('res.partner', string="Buyers")

    @api.constrains('start_date', 'end_date')
    def print_xlsx(self):
        if self.start_date > self.end_date:
            raise ValidationError(_('Start Date must be less than End Date'))
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'buyer_ids': self.buyer_ids.ids,
        }
        return {
            'type': 'ir.actions.act_url',
            'url': '/xlsx_reports?model=estate.report.wizard&options=%s&output_format=xlsx&report_name=Estate Report' % json.dumps(data, default=date_utils.json_default),
            'target': 'self',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        
        # Format the cells
        title_format = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 20, 'bg_color': '#D3D3D3'})
        header_format = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 14, 'bg_color': '#87CEEB', 'border': 1})
        cell_format = workbook.add_format({'font_size': 14, 'border': 1})
        date_format = workbook.add_format({'font_size': 10, 'border': 1})
        
        # Report title
        sheet.merge_range('A1:H2', 'ESTATE REPORT', title_format)
        
        # Date information
        sheet.write('A5', 'From:', header_format)
        sheet.merge_range('B5:C5', data['start_date'], date_format)
        sheet.write('E5', 'To:', header_format)
        sheet.merge_range('F5:G5', data['end_date'], date_format)
        
        # Column headers
        headers = ['Buyer Name', 'Buyer Email', 'Property Accepted', 'Property Sold', 'Property Cancelled',
                   'Offer Accepted', 'Offer Rejected', 
                   'Max Offer', 'Min Offer']
        row = 8
        col = 0
        for header in headers:
            sheet.write(row, col, header, header_format)
            col += 1
        
        # SQL query to get data from property.buyer.report
        query = """
            SELECT
                rp.name as buyer_name,
                rp.email as buyer_email,
                SUM(CASE WHEN ep2.state = 'offer_received' THEN 1 ELSE 0 END) as total_accepted_properties,
                SUM(CASE WHEN ep2.state = 'sold' THEN 1 ELSE 0 END) as total_sold_properties,
                SUM(CASE WHEN ep2.state = 'canceled' THEN 1 ELSE 0 END) as total_cancelled_properties,
                SUM(CASE WHEN ep.status = 'accepted' THEN 1 ELSE 0 END) as total_offer_accepted_properties,
                SUM(CASE WHEN ep.status = 'refused' THEN 1 ELSE 0 END) as total_offer_rejected,
                MAX(ep.price) as max_offer,
                MIN(ep.price) as min_offer
            FROM
                estate_property_offer ep
            JOIN
                res_partner rp ON ep.partner_id = rp.id
            JOIN
                estate_property ep2 ON ep.property_id = ep2.id
            WHERE
                ep.create_date BETWEEN '{start_date}' AND '{end_date}'
        """
        params = {
            'start_date': data['start_date'],
            'end_date': data['end_date']
        }
        if data.get('buyer_ids'):
            query += " AND ep.partner_id IN {buyer_ids}"
            params['buyer_ids'] ='(' + ', '.join(map(str, data['buyer_ids'])) + ')'
        
        query += """
            GROUP BY
                rp.name, rp.email, ep.partner_id
        """
        
        # Replace parameters in the SQL statement to print the full query
        full_query = query.format(**params)
        print("Full SQL Query:", full_query)
        
        # Execute the SQL statement with parameters
        self.env.cr.execute(full_query)
        reports = self.env.cr.dictfetchall()
        
        # Calculate the maximum width for each column
        col_widths = [len(header) for header in headers]
        for report in reports:
            col_widths[0] = max(col_widths[0], len(report['buyer_name'] or ''))
            col_widths[1] = max(col_widths[1], len(report['buyer_email'] or ''))
            col_widths[2] = max(col_widths[2], len(str(report['total_accepted_properties'] or 0)))
            col_widths[3] = max(col_widths[3], len(str(report['total_sold_properties'] or 0)))
            col_widths[4] = max(col_widths[4], len(str(report['total_cancelled_properties'] or 0)))
            col_widths[5] = max(col_widths[5], len(str(report['total_offer_accepted_properties'] or 0)))
            col_widths[6] = max(col_widths[6], len(str(report['total_offer_rejected'] or 0)))
            col_widths[7] = max(col_widths[7], len(str(report['max_offer'] or 0.0)))
            col_widths[8] = max(col_widths[8], len(str(report['min_offer'] or 0.0)))
        
        # Set the width for each column
        for i, width in enumerate(col_widths):
            sheet.set_column(i, i, width + 10)
        
        row += 1
        for report in reports:
            sheet.write(row, 0, report['buyer_name'] or '', cell_format)
            sheet.write(row, 1, report['buyer_email'] or '', cell_format)
            sheet.write(row, 2, report['total_accepted_properties'] or 0, cell_format)
            sheet.write(row, 3, report['total_sold_properties'] or 0, cell_format)
            sheet.write(row, 4, report['total_cancelled_properties'] or 0, cell_format)
            sheet.write(row, 5, report['total_offer_accepted_properties'] or 0, cell_format)
            sheet.write(row, 6, report['total_offer_rejected'] or 0, cell_format)
            sheet.write(row, 7, report['max_offer'] or 0.0, cell_format)
            sheet.write(row, 8, report['min_offer'] or 0.0, cell_format)
            row += 1
        
        # Close the workbook and write data to the response
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()