from odoo import http,api,fields
from odoo.http import request

class orderscontroller(http.Controller):
    def safe_float(value):
        try:
            return float(value)
        except ValueError:
            return 0.0

    @http.route('/order', auth='public', website=True)
    def render_order_form(self,**kwargs):
        students = request.env['library.students'].sudo().search([])
        books = request.env['library.book'].sudo().search([])
        date_today=fields.Datetime.now()

        return request.render('school_library.library_order_web_form', {
            'students': students,
            'books':books,
            'order_date':date_today
           })

    @http.route('/order_submit', auth='public',website=True)
    def render_order_submit(self, **kwargs):
     try:
         #total_price = kwargs.get('total_price')
         discount = kwargs.get('discount',0)

         #total_price = self.safe_float(total_price)
         #discount = self.safe_float(discount)

         #total_price_after_disc = total_price * (discount / 100)

         order = request.env['library.book.order'].sudo().create({
            'students_id': kwargs.get('students_id'),
            'order_date': kwargs.get('order_date'),
            'total_books_borrowed': kwargs.get('total_books_borrowed'),
         })
         return request.render('school_library.library_order_web_submit', {
           'success': True,
         })
     except Exception as e:
        return request.render('school_library.library_order_web_submit', {'error': str(e)})

