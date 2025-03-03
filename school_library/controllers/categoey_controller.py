from odoo import http
from odoo.http import request

class categorycontroller(http.Controller):

    @http.route('/category_form',auth='public',website=True)
    def render_category_form(self,**kwargs):
        return request.render('school_library.library_category_web_form',{'error':'All Fields required'})

    @http.route('/submit_category',auth="public",website=True)
    def save_category(self,**kwargs):
        try:
            name=kwargs.get('name')
            description=kwargs.get('description')
            daily_price=kwargs.get('daily_price')


            category= request.env['library.book.category'].sudo().create(
                {
                    'name':name,
                    'description':description,
                    'daily_price':daily_price
                }
            )

            return request.render('school_library.library_category_web_form',{'success':True})


        except Exception as e:
            return request.render('school_library.library_category_web_form',{'error': str(e)})

    @http.route('/categories', auth='public', website=True)
    def display_authors(self):
        categories = request.env['library.book.category'].sudo().search([])

        return request.render('school_library.library_categories_list', {
            'categories': categories
        })
