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
    invoice_date = fields.Datetime(string="Invoice Date",default=fields.Datetime.now())

    total_price = fields.Float(string='Total Price', compute="_compute_total_price",store=True,default=0)
    total_price_after_disc = fields.Float(string='Total Price after discount ', compute="_compute_total_price",store=True,default=0)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    discount=fields.Float(name="discount",string="Discount",compute="_compute_total_price",default=0)
    total_days=fields.Float(string='Total days', compute="_compute_total_price",default=0)
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

    order_line_ids = fields.One2many('library.book.order.line', 'order_id', string="Order Lines",ondelete='cascade')

    order_reference = fields.Char(
        string="Order Reference",
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('library.book.order.sequence')
      )

    def action_report(self):
        self.invoice_date = fields.Datetime.now()
        report_action = self.env.ref('school_library.action_report_library_order')
        return report_action.report_action(self)


    def print_invoice(self):
        partner_id=self.students_id.user_id
        invoice_lines=[]
        for lin in self.order_line_ids:
            invoice_lines.append((0,0,{
                'product_id':lin.book_id.product_id.id,
                'name':lin.book_id.name,
                'quantity':lin.quantity,
                'price_unit':lin.book_id.daily_price,
                'discount':self.students_id.special_discount
            }))

        invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': partner_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': invoice_lines,
                'currency_id': self.currency_id.id,
                'amount_residual': self.total_price,

            #when i am trying to add other fields it stop working
            }
        invoice = self.env['account.move'].create(invoice_vals)
        invoice.action_post()
        return {
                'type': 'ir.actions.act_window',
                'name': 'Invoice',
                'res_model': 'account.move',
                'res_id': invoice.id,
                'view_mode': 'form',
                'target': 'current',
        }

    @api.constrains('return_date', 'order_date','order_line_ids')
    def _check_return_date_and_status2(self):#see the other options for api
        for record in self:
            if record.return_date and record.return_date < record.order_date:
                raise ValidationError("The return date cannot be earlier than the order date.")
            if record.order_date and (fields.Datetime.now() - record.order_date) > timedelta(days=15):
                record.status = 'overdue'
            elif record.return_date :
                record.status = 'returned'
            elif not record.return_date and not (fields.Datetime.now() - record.order_date) > timedelta(days=15):
                record.status = 'borrowed'
            elif not record.status and record.return_date  and record.return_date  > fields.Datetime.now():
                record.status = 'borrowed'
            if not record.order_line_ids:
                record.status='draft'

     #new task 1
    @api.depends('order_line_ids.quantity')
    def _compute_total_books_borrowed(self):
        for order in self:#no need
            order.total_books_borrowed = sum(line.quantity for line in order.order_line_ids)


    #new task 2
    @api.depends('return_date','order_line_ids.total_price_per_day')
    def _compute_total_price(self):
        for order in self:
          if order.return_date:
            order.total_days=(order.return_date - order.order_date).days
            order.total_price = sum(line.total_price_per_day for line in order.order_line_ids) *  order.total_days
            order.total_price_after_disc=order.total_price - (order.total_price * order.students_id.special_discount)
            order.discount=order.students_id.special_discount
          else:
            order.total_price=0
            order.total_days=0
            order.discount=0

            # new task 1
    @api.depends('status')
    def _compute_status_bar(self):
       for order in self:
            order.status_bar = order.status
     #  self[0].statuse_bar=self[0].status

    @api.model
    def create(self, vals):
        res = super(LibraryBookOrder, self).create(vals)
        if res.students_id:
            res.students_id.compute_student_order()
        return res

    def write(self, vals):
        res = super(LibraryBookOrder, self).write(vals)
        for order in self:
            if order.students_id:
                order.students_id.compute_student_order()
        return res
