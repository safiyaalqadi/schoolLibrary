import datetime

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
    product_id = fields.Many2one('product.product', string="Product")

    @api.model
    def create(self, vals):
        if 'product_id' not in vals:
            product_vals = {
                'name': vals.get('name'),
                'type': 'service',
                'list_price': vals.get('daily_price', 0.0),
                'default_code': vals.get('isbn', ''),
                'description': vals.get('description', ''),
                'categ_id':self.env.ref('product.product_category_all').id,
                'currency_id': vals.get('currency_id', self.env.company.currency_id.id),
            }

            existing_product_template = self.env['product.template'].search([
                ('name', '=', vals.get('name')),
                ('default_code', '=', vals.get('isbn'))
            ], limit=1)
            if existing_product_template:
                product = self.env['product.product'].search([
                    ('product_tmpl_id', '=', existing_product_template.id)
                ], limit=1)
                vals['product_id'] = product.id
            else:
              product = self.env['product.product'].create(product_vals)
              vals['product_id'] = product.id

        return super(LibraryBook, self).create(vals)


    @api.depends('order_line_ids')
    def _compute_history_price(self):
       for record in self:
           record.total_price_history = sum((line.total_price_in_order-(line.total_price_in_order * (line.order_id.students_id.special_discount/100))) for line in record.order_line_ids)
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


    @api.constrains('published_date')
    def _check_date(self):
        for record in self:
           if record.published_date>= datetime.date.today():
               raise ValidationError("Publish date can't be in future")