# feedback_form/models/feedback.py
from odoo import models, fields, _

class Feedback(models.Model):
    _name = 'website.user.feedback'
    _description = 'Feedback Form'

    description = fields.Text(string=_('Description'), required=True)
    create_date = fields.Datetime(string=_('Created At'), default=fields.Datetime.now, readonly=True)