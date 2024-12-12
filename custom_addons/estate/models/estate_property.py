from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

from datetime import datetime, timedelta

# create a model estate.property for the estate module
class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Real Estate Property'
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)', 'The expected price must be positive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be positive.'),
    ]
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # define a method to compute available date
    def _get_default_availability(self):
        return datetime.today() + timedelta(days=90)
    
    code = fields.Char(string='Code', readonly=True)
    name = fields.Char(string='Title', required=True, default='Empty Title', tracking=True)
    description = fields.Text(string='Description', tracking=True)
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(string='Available From', copy=False, default=lambda self: datetime.today() + timedelta(days=90), tracking=True)
    expected_price = fields.Monetary(string='Expected Price', required=True, currency_field='currency_id', default=0, tracking=True)
    selling_price = fields.Monetary(string='Selling Price', currency_field='currency_id', copy=False, default=0, tracking=True)
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area')
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ], string='Garden Orientation')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.ref('base.VND').id, readonly=True, required=True)
    active = fields.Boolean(string='Active', default=True)
    
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ], string='Status', default='new', copy=False, required=True, tracking=True)
    property_type_id = fields.Many2one(
        'estate.property.type', 
        string='Property Type', 
        required=True, 
        default=lambda self: self.env['estate.property.type'].search([], limit=1).id
    )
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False, tracking=True)
    seller_id = fields.Many2one('res.users', string='Seller', tracking=True)
    total_area = fields.Integer(string='Total Area', compute='_compute_total_area', store=True)
    best_price = fields.Monetary(string='Best Price', currency_field='currency_id', compute='_compute_best_price', store=True)
    reason_cancel = fields.Text(string='Reason for Cancellation', tracking=True)
    
    def action_set_sold(self):
        self.ensure_one()
        if self.state == 'canceled':
            raise UserError(_('A canceled property cannot be set as sold.'))
        self.state = 'sold'

    def action_set_canceled(self):
        self.ensure_one()  # Ensure only one record is selected
        if self.state == 'sold':
            raise UserError(_('A sold property cannot be canceled.'))
        self.state = 'canceled'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reason for Cancellation',
            'res_model': 'estate.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_reason_cancel': self.reason_cancel,
                'active_id': self.id,
                'active_model': self._name,
            }
        }
    
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        # Sum the living area and garden area to get the total area
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')    
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped('price'), default=0)

    @api.onchange('garden')
    def _onchange_garden(self):
        for record in self:
            if not record.garden:
                record.garden_area = 0
                record.garden_orientation = False
    
    @api.onchange('date_availability')
    def _onchange_date_availability(self):
        for record in self:
            if record.date_availability and record.date_availability < fields.Date.today():
                return {
                    'warning': {
                        'title': _("Invalid Date"),
                        'message': _("The availability date cannot be in the past."),
                    }
                }
                     
    @api.constrains('date_availability')
    def _check_date_availability(self):
        for record in self:
            if record.date_availability and record.date_availability < fields.Date.today(): 
                raise ValidationError(_('The availability date cannot be in the past.'))
    
    # Add a python constraint so that the selling price cannot be lower than 90% of the expected price.
    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            # Skip records that are not created yet
            if not record.id:
                continue
            if record.selling_price < record.expected_price * 0.9:
                raise ValidationError(_('The selling price cannot be lower than 90% of the expected price.'))
    
    @api.model
    def create(self, vals):
        # Check if the sequence exists, if not, create it
        sequence = self.env['ir.sequence'].search([('code', '=', 'estate.property')], limit=1)
        if not sequence:
            sequence = self.env['ir.sequence'].create({
                'name': 'Estate Property Code',
                'code': 'estate.property',
                'prefix': 'EPT',
                'padding': 5,
                'number_increment': 1,
                'number_next': 1,
            })
        if vals.get('code', 'New') == 'New':
            vals['code'] = sequence.next_by_id() or 'New'
        return super(EstateProperty, self).create(vals)
    
    def check_offer_status(self):
        for record in self:
            accepted_offers = record.offer_ids.filtered(lambda o: o.status == 'accepted')
            if len(accepted_offers) == len(record.offer_ids):
                record.write({'state': 'offer_accepted'})

    def action_view_accepted_offers(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Accepted Offers',
            'view_mode': 'tree,form',
            'res_model': 'estate.property.offer',
            'domain': [('property_id', '=', self.id), ('status', '=', 'accepted')],
            'context': {'default_property_id': self.id},
        }
    
    def get_accepted_offer_count(self):
        """
        Calculate the number of accepted offers for the estate property.

        This method ensures that the operation is performed on a single record.
        It filters the offers related to the property to count only those with the status 'accepted'.

        Returns:
            int: The number of accepted offers.
        """
        self.ensure_one()
        return len(self.offer_ids.filtered(lambda o: o.status == 'accepted'))
    
    def unlink(self):
        """
        Unlink (delete) records if they are in 'new' or 'canceled' state.

        Raises:
            UserError: If the record's state is not 'new' or 'canceled'.

        Returns:
            bool: True if the operation was successful, otherwise raises an error.
        """
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise UserError(_('You cannot delete a property that is not in "New" or "Canceled" state.'))
        return super(EstateProperty, self).unlink()