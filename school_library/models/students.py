from odoo import api,models, fields
from odoo.exceptions import ValidationError
import re

class LibraryMember(models.Model):
    _name = 'library.students'
    _description = 'Library student'
    _inherit = ['mail.thread']

    name = fields.Char(string="student Name", required=True,tracking=True)
    email = fields.Char(string="Email",tracking=True)
    phone = fields.Char(string="Phone",tracking=True)
    address = fields.Text(string="Address",tracking=True)
    order_ids = fields.One2many('library.book.order', 'students_id', string="Book Orders")

    @api.constrains('email')
    def _check_email(self):
      for record in self:
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if record.email:
            if not re.match(email_regex, record.email):
                raise ValidationError("The email address is not valid. Please enter a valid email.")

    @api.constrains('phone')
    def _check_phone(self):
       for record in self:
          phone_regex = r'^\+?[\d\s\-]{7,15}$'
          if record.phone:
            if not re.match(phone_regex, record.phone):
                raise ValidationError("The phone number is not valid. Please enter a valid phone number.")