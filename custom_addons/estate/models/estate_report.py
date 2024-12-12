from odoo import models, fields, api

class PropertyBuyerReport(models.Model):
    _name = 'property.buyer.report'
    _description = 'Property Buyer Report'
    _auto = False

    buyer_id = fields.Many2one('res.partner', string='Buyer')
    buyer_name = fields.Char(related='buyer_id.name', string='Buyer Name')
    buyer_email = fields.Char(related='buyer_id.email', string='Buyer Email')
    total_accepted_properties = fields.Integer(string='Property Accepted')
    total_sold_properties = fields.Integer(string='Property Sold')
    total_cancelled_properties = fields.Integer(string='Property Cancelled')
    total_offer_accepted_properties = fields.Integer(string='Offer Accepted')
    total_offer_rejected = fields.Integer(string='Offer Rejected')
    max_offer = fields.Float(string='Max Offer')
    min_offer = fields.Float(string='Min Offer')

    @api.model
    def init(self):
        self._cr.execute("""
            CREATE OR REPLACE VIEW property_buyer_report AS (
                SELECT
                    row_number() OVER () as id,
                    rp.id as buyer_id,
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
                    ep.status IN ('accepted', 'refused', 'new')
                GROUP BY
                    rp.id, rp.name, rp.email
            )
        """)