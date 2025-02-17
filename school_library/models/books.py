from odoo import api,models, fields
from odoo.exceptions import ValidationError
import re

from odoo.odoo.tools.populate import compute
class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _inherit = ['mail.thread']

    name = fields.Char(string="Title", required=True,tracking=True)
    author_id = fields.Many2one('library.author', string="Author", required=True)
    isbn = fields.Char(string="ISBN", required=True,tracking=True)
    published_date = fields.Date(string="Published Date",tracking=True)
    pages = fields.Integer(string="Number of Pages",tracking=True)
    description = fields.Text(string="Description",tracking=True)
    category_id = fields.Many2one('library.book.category', string="Category",tracking=True)
    available_copies = fields.Integer(string="Available Copies", default=1,tracking=True)
    available_copies_to_order=fields.Integer(string="Available Copies",compute='_compute_borrowed_copies',default=1,store=True)
    borrowed_copies = fields.Integer(string="Borrowed Copies", compute="_compute_borrowed_copies", store=True)
    order_line_ids = fields.One2many('library.book.order.line', 'book_id', string="Order Lines")
    status=fields.Selection([#new task 1
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('out_of_stock', 'Out of Stock')
    ], string='Status', default='available',compute='_compute_status')
    daily_price=fields.Float(string="Daily borrow Price",compute='_compute_daily_price')
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    total_price_history=fields.Float(string="Daily borrow Price",compute='_compute_history_price',store=True,default=0)
    order = fields.Integer('Order', default=-1)



    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if limit == 10 and 'total_price_history desc' in order:
            args.append(('total_price_history', '>', 0))
        return super(LibraryBook, self).search(args, offset, limit, order, count)

    @api.model
    def get_top_10_books_ids(self):
        top_10_books = self.env['library.book'].search([], order='total_price_history', limit=10)
        if top_10_books:
            return top_10_books
        else:
            return []

    @api.depends('order_line_ids')
    def _compute_history_price(self):
       for record in self:
           record.total_price_history = sum(line.total_price_in_order for line in record.order_line_ids)
           books_ordered = record.search([], order='total_price_history desc', limit=10)
           if books_ordered :
              for idx, book in enumerate(books_ordered):
                  book.order = idx + 1
              all_books = self.search([('id', 'not in', books_ordered.ids)])
              all_books.write({'order': 0})


    @api.depends('category_id')
    def _compute_daily_price(self):
        for record in self:
          record.daily_price=record.category_id.daily_price

    @api.depends('order_line_ids.quantity','order_line_ids.order_id.status')
    def _compute_borrowed_copies(self):
        for record in self:
            borrowed_count = sum(line.quantity for line in record.order_line_ids if line.order_id.status != 'returned')
            record.borrowed_copies = borrowed_count
            record.available_copies_to_order=record.available_copies - record.borrowed_copies

    @api.depends('available_copies', 'borrowed_copies')
    def _compute_status(self):
        for record in self:
            if record.borrowed_copies >= record.available_copies:
                record.status = 'out_of_stock'
            elif record.borrowed_copies > 0:
                record.status = 'borrowed'
            else:
                record.status = 'available'


    @api.constrains('name', 'isbn')
    def _check_book_unique(self):
        for record in self:
            existing_book = self.search([
                ('name', '=', record.name),
                ('isbn', '=', record.isbn),
                ('id', '!=', record.id)
            ], limit=1)

            if existing_book:
                raise ValidationError(
                    "A book with the title '%s' and ISBN '%s' already exists." % (record.name, record.isbn))

    @api.constrains('isbn')
    def _check_isbn(self):
        for record in self:
            isbn = record.isbn
            isbn_10_pattern = r'^\d{9}[\dX]$'
            isbn_13_pattern = r'^\d{13}$'
            if not re.match(isbn_10_pattern, isbn) and not re.match(isbn_13_pattern, isbn):
                raise ValidationError("The ISBN number is not valid. Please enter a valid ISBN-10 or ISBN-13.")


