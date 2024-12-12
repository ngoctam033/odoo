from odoo import models, fields

class EstateUser(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many(
        'estate.property', 
        'seller_id', 
        string='Salesperson Properties',
        domain=[('date_availability', '>=', fields.Date.today())]
    )