from odoo import api,models, fields
from odoo.exceptions import ValidationError

class CustomInvoice(models.Model):
    _inherit = 'account.move'

    total_price_in_order = fields.Float(string="Total Price in order", default=0)#each line total in order
    total_price_per_day = fields.Float(string="Total Price Per day")#bassed on quantity each line iin one day
    total_days=fields.Float(string='Total days',default=0)
    total_price = fields.Float(string='Total Price', default=0)#sum of all

