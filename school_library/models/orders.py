from odoo import api , models , fields
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class LibraryBookOrder(models.Model):
    _name = 'library.book.order'
    _description = 'Library Book Order'
    _inherit = ['mail.thread']

    students_id = fields.Many2one('library.students', string="Library student", tracking=True,required=True)
    order_date = fields.Datetime(string="Order Date", default=fields.Datetime.now,tracking=True)
    return_date = fields.Datetime(string="Return Date",tracking=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ], default='draft', string="Order Status",tracking=True)
    order_line_ids = fields.One2many('library.book.order.line', 'order_id', string="Order Lines")

    order_reference = fields.Char(
        string="Order Reference",
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('library.book.order.sequence')
    )

    #def write(self, vals): trying go make the form save auto befor start typing in the nested one
       # res = super(LibraryBookOrder, self).write(vals)
      #  self.sudo().write(vals)
       # return res

    @api.constrains('return_date', 'status')
    def _check_return_date_and_status(self):
        for record in self:
            if not record.return_date and record.status != 'borrowed':
                raise ValidationError("If no return date is entered, the status must be 'borrowed'.")

    @api.constrains('return_date', 'order_date')
    def _check_return_date_and_status(self):
        for record in self:
            if record.return_date and record.return_date < record.order_date:
                raise ValidationError("The return date cannot be earlier than the order date.")

            if not record.return_date and record.status == 'returned':
                raise ValidationError("If no return date is entered, the status must be 'borrowed' Or 'overdue'.")

            if  record.return_date and record.status == 'borrowed':
                raise ValidationError("If return date is entered, the status must be 'returned' .")
