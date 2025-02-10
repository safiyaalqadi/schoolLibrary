from odoo import models, fields,api
from odoo.exceptions import ValidationError

class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Library Author'
    _inherit = ['mail.thread']

    name = fields.Char(string="Author Name", required=True,tracking=True)
    biography = fields.Text(string="Biography",tracking=True)
    book_ids = fields.One2many('library.book', 'author_id', string="Books")

    @api.constrains('name')
    def _check_author_name(self):
        existing_book=self.search([('name','=',self.name),('id','!=',self.id)],limit=1)
        if existing_book:
           raise ValidationError("The author '%s' already exists." % self.name)

