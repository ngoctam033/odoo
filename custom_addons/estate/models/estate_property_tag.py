from odoo import models, fields, _

# create a model estate.property.tag for the estate module
class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Real Estate Property Tag'
    # A property tag name must be unique
    _sql_constraints = [
        ('tag_name_unique', 'UNIQUE (name)', 'The tag name must be unique.')
    ]

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color')