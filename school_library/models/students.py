from odoo import api,models, fields
from odoo.exceptions import ValidationError
import re

from odoo.odoo.tools.populate import compute


class LibraryMember(models.Model):
    _name = 'library.students'
    _description = 'Library student'
    _inherit = ['mail.thread']

    name = fields.Char(string="student Name", required=True,tracking=True)
    email = fields.Char(string="Email",tracking=True)
    phone = fields.Char(string="Phone",tracking=True)
    address = fields.Text(string="Address",tracking=True)
    order_ids = fields.One2many('library.book.order', 'students_id', string="Book Orders")
    user_id = fields.Many2one('res.users', string='Assigned User', tracking=True)
    order = fields.Integer(string='order',compute='compute_student_order',store=True,default=-1)# order of student in top ten not the order of books
    rank=fields.Integer(string='rank',default=100)#rank of student in top ten

    @api.depends('order_ids')
    def compute_student_order(self):
        for record in self:
            returned_orders = record.order_ids.filtered(lambda order: order.status == 'returned')
            if returned_orders:
                record.order = sum(line.quantity for line in returned_orders.order_line_ids)
                students_rank = record.search([], order='order desc', limit=10)
                if students_rank:
                    for idx, student in enumerate(students_rank):
                        student.rank = idx + 1
                all_student = self.search([('id', 'not in', students_rank.ids)])
                all_student.write({'rank': 100})
            else:
                record.order=0

    @api.depends('order')
    def compute_rank(self):
        for record in self:
           ranks = record.search([], order='order desc', limit=10)
           if ranks:
             for idx, student in enumerate(ranks):
                student.rank=idx+1
           all_student = self.env['library.students'].search([('id', 'not in', ranks.ids)])
           all_student.write({'rank': 0})

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