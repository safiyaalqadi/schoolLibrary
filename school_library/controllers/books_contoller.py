from odoo import http,api
from odoo.http import request


class BookController(http.Controller):

    @http.route('/book_form', auth='public', website=True)
    def render_auth_form(self, **kwargs):
        return request.render('school_library.library_book_web_form',{'error': 'All fields are required.'})

    @http.route('/submit_book', auth="public", website=True)
    def save_author(self, **kwargs):
      try:
         name = kwargs.get('name')
         isbn = kwargs.get('isbn')
         author_id = kwargs.get('author_id')
         published_date = kwargs.get('published_date')
         pages = kwargs.get('pages')
         description = kwargs.get('description')
         category_id = kwargs.get('category_id')
         available_copies = kwargs.get('available_copies')
         order_line_ids = kwargs.get('order_line_ids')


         book = request.env['library.book'].sudo().create({
            'name': name,
            'isbn': isbn,
            'author_id':author_id,
            'published_date':published_date,
            'pages':pages,
            'description':description,
            'category_id':category_id,
            'available_copies':available_copies,
            'order_line_ids':order_line_ids
          })
         return request.render('school_library.library_book_web_form',{'success':True})

      except Exception as e:
         return request.render('school_library.library_book_web_form', {'error': str(e)})



