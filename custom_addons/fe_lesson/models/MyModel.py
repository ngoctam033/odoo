from odoo import models, fields

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Simple Model'

    name = fields.Char(string='Name', default='New')
    color = fields.Integer(string='Color', default=2)
    date = fields.Date(string='Date', default=fields.Date.today)