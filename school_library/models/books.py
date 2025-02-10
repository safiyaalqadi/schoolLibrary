from odoo import api,models, fields
from odoo.exceptions import ValidationError
import re

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
    order_line_ids = fields.One2many('library.book.order.line', 'book_id', string="Order Lines")

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


