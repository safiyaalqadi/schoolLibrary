from odoo import api,models, fields
from odoo.exceptions import ValidationError

class LibraryBookCategory(models.Model):
    _name = 'library.book.category'
    _description = 'Library Book Category'
    _inherit = ['mail.thread']

    name = fields.Char(string="Category Name", required=True,tracking=True)
    description = fields.Text(string="Category Description",tracking=True)
    book_ids = fields.One2many('library.book', 'category_id', string="Books")
    daily_price= fields.Float(string="Daily borrow Price")
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)

    @api.constrains('name')
    def _check_category_name_unique(self):
        existing_category = self.search([('name', '=', self.name), ('id', '!=', self.id)], limit=1)
        if existing_category:
            raise ValidationError("A category with the name '%s' already exists." % self.name)

