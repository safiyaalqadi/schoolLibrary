from odoo import api,models, fields
from odoo.exceptions import ValidationError

class CustomInvoice(models.Model):
    _inherit = ['account.move']

    order_date = fields.Datetime(string="Order Date")
    return_date = fields.Datetime(string="Return Date")
    total_days= fields.Float(string="days",compute="_compute_days")
    price_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_price_total',default=0)

    @api.depends('order_date','return_date')
    def _compute_days(self):
        for record in self:
            if record.return_date and record.order_date:
              record.total_days = (record.return_date - record.order_date).days
            else:
                record.total_days=0

    @api.depends('invoice_line_ids')
    def _compute_price_total(self):
        if(self.invoice_line_ids):
          for line in self.invoice_line_ids:
             price_total = line.quantity * line.price_unit * self.total_days
             if line.discount:
                price_total -= price_total * (line.discount / 100)

             self.price_total += price_total

        else:
            self.price_total=0

