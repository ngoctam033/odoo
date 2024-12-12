from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# create a model estate.property.type for the estate module
class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Type'

    name = fields.Char(string='Property Type', required=True)
    # add offer_ids field
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='Offers')
    # add offer_count field
    offer_count = fields.Integer(string='Offer Count', compute='_compute_offer_count')

    @api.onchange('name')
    def _onchange_name(self):
        for record in self:
            if record.name:
                # Find all records with the same name
                duplicate_count = self.search_count([('name', '=ilike', record.name)])
                if duplicate_count > 0:
                    return {
                        'warning': {
                            'title': _('Duplicate Name Warning onchange'),
                            'message': _('The property type name "{}" already exists. Please choose a different name.').format(record.name),
                        }
                    }

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            if record.name:
                # find all records with the same name(not case sensitive)
                duplicate_count = self.search_count([('name', '=ilike', record.name)])
                if duplicate_count > 1:
                    raise ValidationError(_('The property type name "{}" already exists. Please choose a different name.').format(record.name))
                
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)