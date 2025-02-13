from odoo import api,models, fields
from odoo.exceptions import ValidationError

class LibraryBookOrderLine(models.Model):
    _name = 'library.book.order.line'
    _description = 'Library Book Order Line'
    _inherit = ['mail.thread']

    order_id = fields.Many2one('library.book.order', string="Order", required=True)
    book_id = fields.Many2one('library.book', string="Book", required=True)
    quantity = fields.Integer(string="Quantity", default=1,tracking=True)
    total_price_per_day=fields.Float(string="Total Price Per day",compute="_compute_total_price_for_one_line",store=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    total_price_in_order=fields.Float(string="Total Price in order",compute="_check_total_for_each_line",default=0)

    @api.depends('order_id')
    def _check_total_for_each_line(self):
        for record in self:
            if record.order_id.return_date :
                record.total_price_in_order=record.order_id.total_days*record.total_price_per_day
            else:
                record.total_price_in_order=0

    @api.depends('book_id','quantity')
    def _compute_total_price_for_one_line(self):
        for record in self:
            if record.book_id:
                if record.book_id.daily_price and record.quantity:
                   record.total_price_per_day=record.book_id.daily_price*record.quantity
            else :
                record.total_price_per_day=0

    @api.constrains('quantity', 'book_id')
    def _check_quantity_against_available_copies(self):
        for record in self:
            if record.quantity <1:
                raise ValidationError("quantity can't be less than 0ne")
            if record.book_id:
                total_ordered_quantity = sum(line.quantity for line in record.book_id.order_line_ids if
                                             line.order_id.status not in ['returned', 'Returned'])
                #total_ordered_quantity += record.quantity  it gives duple quantity
                if total_ordered_quantity > record.book_id.available_copies:
                    raise ValidationError(
                        f"The total quantity ordered for the book '{record.book_id.name}' exceeds the available copies ({record.book_id.available_copies}) .")

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.book_id:
            self.book_id._compute_borrowed_copies()
        if self.order_id:
            self.order_id._compute_total_books_borrowed()