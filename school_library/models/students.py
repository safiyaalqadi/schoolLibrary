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
    order = fields.Integer(string='order books sum',compute='compute_student_order',store=True,default=-1)
    rank=fields.Integer('Rank',default=-1,compute="compute_rank",store=True)
    special_discount = fields.Float(string="Special Discount", compute='_compute_special_discount',default=0)
    total_Student=fields.Float(string="Total",compute="_compute_total_student")
    total_Student_after_discount=fields.Float(string="Total after discount",compute="_compute_special_discount")
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    partner_id=fields.Many2one('res.partner',string="partner User")

    @api.depends('order_ids')
    def _compute_total_student(self):
        for record in self:
            record.total_Student=sum(line.total_price for line in record.order_ids )

    @api.depends('rank','total_Student')
    def _compute_special_discount(self):
        for record in self:
            if 1 <= record.rank <= 10:
                record.special_discount = 0.2

            else:
                record.special_discount = 0.0
        record.total_Student_after_discount = (
                record.total_Student -
                (record.total_Student * record.special_discount)
                                               )

    @api.depends('order_ids')
    def compute_student_order(self):
        for record in self:
            returned_orders = record.order_ids.filtered(lambda order: order.status == 'returned')
            if returned_orders:
                total_quantity = 0
                for order in returned_orders:
                    for line in order.order_line_ids:
                        total_quantity += line.quantity
                record.order = total_quantity
            else:
                record.order = 0

    @api.depends('order')
    def compute_rank(self):
        for record in self:
            all_students = self.search([], order='order desc')
            for idx, student in enumerate(all_students):
                if idx < 10:
                    student.rank = idx + 1
                else:
                    student.rank = 100




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