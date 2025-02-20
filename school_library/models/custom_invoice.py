from odoo import api,models, fields
from odoo.exceptions import ValidationError

class CustomInvoice(models.Model):
    _inherit = ['account.move']

    order_date = fields.Datetime(string="Order Date")
    return_date = fields.Datetime(string="Return Date")
    total_days= fields.Float(string="days",compute="_compute_days")

    @api.depends('order_date','return_date')
    def _compute_days(self):
        for record in self:
            if record.return_date and record.order_date:
              record.total_days = (record.return_date - record.order_date).days
            else:
                record.total_days=0



