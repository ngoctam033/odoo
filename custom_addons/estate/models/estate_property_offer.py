from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import timedelta

# create a model estate.property.offer for the estate module
class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'
    _sql_constraints = [
        ('check_offer_price', 'CHECK(price >= 0)', 'The offer price must be positive.'),
    ]

    property_id = fields.Many2one(
        'estate.property', 
        string='Property', 
        required=True,
    )

    partner_id = fields.Many2one(
        'res.partner', 
        string='Partner', 
        required=True, 
    )

    price = fields.Monetary(string='Price', currency_field='currency_id', required=True)

    property_type_id = fields.Many2one(
        'estate.property.type', 
        string='Property Type', 
        related='property_id.property_type_id', 
        store=True
    )

    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
        ('new', 'New')
    ], string='Status', default='new')

    validity = fields.Integer(string='Validity', required=True, default=7)
    create_date = fields.Date(string='Creation Date', default=fields.Date.context_today)
    date_deadline = fields.Date(string='Deadline', required=True, compute='_compute_date_deadline')
    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency', 
        default=lambda self: self.env.ref('base.VND').id, 
        readonly=True, 
        required=True
    )

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.context_today(self) + timedelta(days=record.validity)

    @api.onchange('property_id', 'partner_id', 'price', 'status', 'validity')
    def _onchange_status(self):
        for record in self:
            current_status = self.env['estate.property.offer'].browse(record.id).status
            if current_status == 'accepted' and record.status == 'refused':
                record.status = current_status
                return {
                    'warning': {
                        'title': _("Status Warning"),
                        'message': _("Cannot change status from 'Accepted' to 'Refused'."),
                    }
                }
    @api.model
    def default_get(self, fields_list):
        res = super(EstatePropertyOffer, self).default_get(fields_list)
        if self.env.context.get('active_id'):
            property_id = self.env['estate.property'].browse(self.env.context['active_id'])
            res['property_type_id'] = property_id.property_type_id.id
            res['property_id'] = property_id.id
            res['partner_id'] = None
        return res
    
    # override the create method
    # when creating a new offer, change value of field 'state' of property_id to 'offer_received'
    @api.model
    def create(self, vals):
        property_id = vals.get('property_id')
        price = vals.get('price')

        # Check if the offer price is lower than an existing offer
        existing_offers = self.env['estate.property.offer'].search([('property_id', '=', property_id)])
        if any(offer.price > price for offer in existing_offers):
            raise UserError(_('You cannot create an offer with a lower amount than an existing offer.'))

        # Create the offer
        res = super(EstatePropertyOffer, self).create(vals)

        # Set the state of the property to 'offer_received'
        res.property_id.state = 'offer_received'

        # Check if all offers are accepted or refused
        res.property_id.check_offer_status()

        # Update buyer_id if the offer is accepted
        if res.status == 'accepted':
            res.property_id.buyer_id = res.partner_id

        return res
    
    @api.model
    def write(self, vals):
        for record in self:
            if record.status == 'accepted':
                raise UserError(_('Cannot Edit/Delete Offer Accepted'))
        return super(EstatePropertyOffer, self).write(vals)

    @api.model
    def unlink(self):
        for record in self:
            if record.status == 'accepted':
                raise UserError(_('Cannot Edit/Delete Offer Accepted'))
        return super(EstatePropertyOffer, self).unlink()
    
    def action_accept(self):
        for record in self:
            if record.status == 'refused':
                raise UserError(_('A refused offer cannot be accepted.'))
            record.status = 'accepted'
            record.property_id.write({'state': 'offer_accepted'})
            record.property_id.write({'selling_price': record.price})
            record.property_id.buyer_id = record.partner_id

    def action_refuse(self):
        for record in self:
            if record.status == 'accepted':
                raise UserError(_('An accepted offer cannot be refused.'))
            record.status = 'refused'