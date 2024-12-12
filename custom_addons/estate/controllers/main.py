from odoo import http
from odoo.http import content_disposition, request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape
from odoo.http import request, Response
from odoo.exceptions import ValidationError, UserError

import json

class XLSXReportController(http.Controller):
    @http.route('/xlsx_reports', type='http', auth='public', methods=['GET'], csrf=False)
    def get_report_xlsx(self, model, options, output_format, report_name, **kw):
        options = json.loads(options)
        report_obj = request.env[model].sudo()
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[('Content-Type', 'application/vnd.ms-excel'), ('Content-Disposition', content_disposition(report_name + '.xlsx'))]
                )
                report_obj.get_xlsx_report(options, response)
                return response
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
        
class EstatePropertyController(http.Controller):

    @http.route(['/', '/page', '/page/<int:page>'], type='http', auth='public', website=True)
    def list_properties(self, page=1, **kwargs):
        Property = request.env['estate.property'].sudo()
        limit = 12  # Số sản phẩm mỗi trang
        page = int(page)
        offset = (page - 1) * limit

        # Thu thập các tham số tìm kiếm
        domain = []
        name = kwargs.get('name')
        code = kwargs.get('code')
        state = kwargs.get('state')
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')

        if name:
            domain.append(('name', 'ilike', name))
        if code:
            domain.append(('code', 'ilike', code))
        if state:
            domain.append(('state', '=', state))
        if min_price:
            domain.append(('expected_price', '>=', float(min_price)))
        if max_price:
            domain.append(('expected_price', '<=', float(max_price)))

        total_properties = Property.search_count(domain)
        properties = Property.search(domain, offset=offset, limit=limit, order='id desc')

        pager = request.website.pager(
            url='/',
            total=total_properties,
            page=page,
            step=limit,
            scope=5,
            url_args=kwargs,
        )
        print(pager)
        return request.render('estate.property_list_template', {
            'properties': properties,
            'pager': pager,
            'search_params': {
                'name': name or '',
                'code': code or '',
                'state': state or '',
                'min_price': min_price or '',
                'max_price': max_price or '',
            }
        })
    
    @http.route('/', type='http', auth='public', website=True)
    def list_properties_default_page(self, **kwargs):
        return self.list_properties(page=1, **kwargs)
    

    @http.route('/estate/property_detail', type='http', auth='public', website=True)
    def property_detail(self, id, **kwargs):
        property = request.env['estate.property'].sudo().search([('id', '=', id)], limit=1)
        if not property:
            return request.not_found()
        return request.render('estate.property_detail_template', {
            'property': property
        })

    @http.route('/api/estate/property', type='http', auth='public', methods=['GET'], csrf=False)
    def api_list_properties(self, **kwargs):
        try:
            Property = request.env['estate.property'].sudo()
            properties = Property.search([])
            result = []
            for prop in properties:
                result.append({
                    'id': prop.id,
                    'name': prop.name,
                    'description': prop.description,
                    'expected_price': prop.expected_price,
                    'selling_price': prop.selling_price,
                    'state': prop.state,
                    'date_availability': str(prop.date_availability),
                    'bedrooms': prop.bedrooms,
                    'living_area': prop.living_area,
                    'facades': prop.facades,
                    'garage': prop.garage,
                    'garden': prop.garden,
                    'garden_area': prop.garden_area,
                    'garden_orientation': prop.garden_orientation,
                    'currency_id': prop.currency_id.id,
                    'active': prop.active,
                    'property_type_id': prop.property_type_id.id,
                    'buyer_id': prop.buyer_id.id,
                    'seller_id': prop.seller_id.id,
                    'total_area': prop.total_area,
                    'best_price': prop.best_price,
                    'reason_cancel': prop.reason_cancel,
                })
            return Response(
                json.dumps({'status': 'success', 'data': result}),
                content_type='application/json',
            )
        except Exception as e:
            return Response(
                json.dumps({'status': 'error', 'message': str(e)}),
                content_type='application/json',
            )

    @http.route('/api/estate/property/<int:property_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def fetch_property(self, property_id, **kwargs):
        try:
            Property = request.env['estate.property'].sudo()
            prop = Property.browse(property_id)
            if not prop.exists():
                return Response(
                    json.dumps({'status': 'error', 'message': 'Property not found'}),
                    content_type='application/json',
                )
            data = {
                'id': prop.id,
                'name': prop.name,
                'description': prop.description,
                'expected_price': prop.expected_price,
                'selling_price': prop.selling_price,
                'state': prop.state,
                'date_availability': str(prop.date_availability),
                'bedrooms': prop.bedrooms,
                'living_area': prop.living_area,
                'facades': prop.facades,
                'garage': prop.garage,
                'garden': prop.garden,
                'garden_area': prop.garden_area,
                'garden_orientation': prop.garden_orientation,
                'currency_id': prop.currency_id.id,
                'active': prop.active,
                'property_type_id': prop.property_type_id.id,
                'buyer_id': prop.buyer_id.id,
                'seller_id': prop.seller_id.id,
                'total_area': prop.total_area,
                'best_price': prop.best_price,
                'reason_cancel': prop.reason_cancel,
            }
            return Response(
                json.dumps({'status': 'success', 'data': data}),
                content_type='application/json',
            )
        except Exception as e:
            return Response(
                json.dumps({'status': 'error', 'message': str(e)}),
                content_type='application/json',
            )

    @http.route('/api/estate/property', type='json', auth='public', methods=['POST'], csrf=False)
    def add_property(self, **kwargs):
        try:
            # Đọc và phân tích dữ liệu JSON từ yêu cầu
            request_data = json.loads(request.httprequest.data.decode('utf-8'))
            # in ra request_data để xem dữ liệu nhận được
            print(request_data)
            Property = request.env['estate.property'].sudo().create(request_data)
            
            return Response(
                json.dumps({'status': 'success', 'id': property.id}),
                content_type='application/json',
            )
        except (ValidationError, UserError) as ve:
            return Response(
                json.dumps({'status': 'error', 'message': ve.name}),
                content_type='application/json',
            )
        except Exception as e:
            return Response(
                json.dumps({'status': 'error', 'message': str(e)}),
                content_type='application/json',
            )

    @http.route('/api/estate/property/<int:property_id>', type='json', auth='public', methods=['PUT'], csrf=False)
    def modify_property(self, property_id, **kwargs):
        try:
            # Đọc và phân tích dữ liệu JSON từ yêu cầu
            request_data = json.loads(request.httprequest.data.decode('utf-8'))
            
            Property = request.env['estate.property'].sudo()
            prop = Property.browse(property_id)
            if not prop.exists():
                return Response(
                    json.dumps({'status': 'error', 'message': 'Property not found'}),
                    content_type='application/json',
                )
            prop.write(request_data)
            return Response(
                json.dumps({'status': 'success'}),
                content_type='application/json',
            )
        except (ValidationError, UserError) as ve:
            return Response(
                json.dumps({'status': 'error', 'message': ve.name}),
                content_type='application/json',
            )
        except Exception as e:
            return Response(
                json.dumps({'status': 'error', 'message': str(e)}),
                content_type='application/json',
            )

    @http.route('/api/estate/property/<int:property_id>', type='json', auth='public', methods=['PATCH'], csrf=False)
    def partially_update_property(self, property_id, **kwargs):
        try:
            # Đọc và phân tích dữ liệu JSON từ yêu cầu
            request_data = json.loads(request.httprequest.data.decode('utf-8'))
            print(request_data)
            Property = request.env['estate.property'].sudo()
            prop = Property.browse(property_id)
            if not prop.exists():
                return Response(
                    json.dumps({'status': 'error', 'message': 'Property not found'}),
                    content_type='application/json',
                )
            prop.write(request_data)
            return Response(
                json.dumps({'status': 'success'}),
                content_type='application/json',
            )
        except (ValidationError, UserError) as ve:
            return Response(
                json.dumps({'status': 'error', 'message': ve.name}),
                content_type='application/json',
            )
        except Exception as e:
            return Response(
                json.dumps({'status': 'error', 'message': str(e)}),
                content_type='application/json',
            )

    @http.route('/api/estate/property/<int:property_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def remove_property(self, property_id, **kwargs):
        try:
            Property = request.env['estate.property'].sudo()
            prop = Property.browse(property_id)
            print(prop)
            if not prop.exists():
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Property not found'}),
                    headers={'Content-Type': 'application/json'},
                )
            prop.unlink()
            return request.make_response(
                    json.dumps({'status': 'success'}),
                    headers={'Content-Type': 'application/json'},
                )
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json'},
            )