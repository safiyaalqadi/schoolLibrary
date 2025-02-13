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
    ], default='draft', string="Order Status",tracking=True ,  compute='_compute_status_bar',store=True)
    total_books_borrowed = fields.Integer(
        string="Total Books Borrowed",
        compute='_compute_total_books_borrowed',
        store=True
    )
    status_bar = fields.Selection([
        ('draft', 'Draft'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ], string="Status", default='draft', compute='_compute_status_bar',store=True)

    order_line_ids = fields.One2many('library.book.order.line', 'order_id', string="Order Lines")

    order_reference = fields.Char(
        string="Order Reference",
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('library.book.order.sequence')
      )



    @api.constrains('return_date', 'order_date','order_line_ids')
    def _check_return_date_and_status2(self):
        for record in self:
            if record.return_date and record.return_date < record.order_date:
                raise ValidationError("The return date cannot be earlier than the order date.")
            if record.order_date and (fields.Datetime.now() - record.order_date) > timedelta(days=15):
                record.status = 'overdue'
            if  record.return_date :
                record.status = 'returned'
            if not record.return_date and not (fields.Datetime.now() - record.order_date) > timedelta(days=15):
                record.status = 'borrowed'
            if not record.status and record.return_date  and record.return_date  > fields.Datetime.now():
                record.status = 'borrowed'
            if not record.order_line_ids:
                record.status='draft'

     #new task 1
    @api.depends('order_line_ids.quantity')
    def _compute_total_books_borrowed(self):
        for order in self:
            order.total_books_borrowed = sum(line.quantity for line in order.order_line_ids)

    # new task 1
    @api.depends('status')
    def _compute_status_bar(self):
        for order in self:
            order.status_bar = order.status


