from email.policy import default

from odoo import api,models, fields
from odoo.exceptions import ValidationError

class CustomInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    subtotal_price_days=fields.Monetary(
        string='Subtotal days',
        compute='_compute_totals_days', store=True,
        currency_field='currency_id',
        default=0
    )

    @api.depends('quantity')
    def _compute_totals_days(self):
        for record in self:
            if record.price_subtotal:
              record.subtotal_price_days=record.price_subtotal*record.move_id.total_days
            else:
                record.subtotal_price_days=0






