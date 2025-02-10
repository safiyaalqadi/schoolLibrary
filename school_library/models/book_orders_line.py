from odoo import api,models, fields
from odoo.exceptions import ValidationError

class LibraryBookOrderLine(models.Model):
    _name = 'library.book.order.line'
    _description = 'Library Book Order Line'
    _inherit = ['mail.thread']

    order_id = fields.Many2one('library.book.order', string="Order", required=True)
    book_id = fields.Many2one('library.book', string="Book", required=True)
    quantity = fields.Integer(string="Quantity", default=1,tracking=True)


    @api.constrains('quantity', 'book_id')
    def _check_quantity_against_available_copies(self):
        for record in self:
            if record.book_id:
                total_ordered_quantity = sum(line.quantity for line in record.book_id.order_line_ids if
                                             line.order_id.status not in ['returned', 'Returned'])
                #total_ordered_quantity += record.quantity  it gives duple quantity
                if total_ordered_quantity > record.book_id.available_copies:
                    raise ValidationError(
                        f"The total quantity ordered for the book '{record.book_id.name}' exceeds the available copies ({record.book_id.available_copies}) .")