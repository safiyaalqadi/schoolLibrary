from odoo import http,api
from odoo.http import request


class BookController(http.Controller):

    @http.route('/book_form', auth='public', website=True)
    def render_auth_form(self, **kwargs):
        return request.render('school_library.library_book_web_form',{'error': 'All fields are required.'})

    @http.route('/books', auth='public', website=True)
    def display_books(self):
        books = request.env['library.book'].sudo().search([])
        categories=request.env['library.book.category'].search([])

        return request.render('school_library.library_books_list', {
            'books': books,
            'categories': categories
        })

    @http.route('/submit_book', auth="public", website=True)
    def save_Book(self, **kwargs):
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

    @http.route('/filter_books', auth="public", website=True)
    def filter_books(self, category_id=None):
        domain = []
        if category_id:
            domain = [('category_id.id', '=', int(category_id))]

        books = request.env['library.book'].search(domain)

        return request.render('school_library.library_books_list', {
            'books': books,
            'categories': request.env['library.book.category'].search([]),
        })

    @http.route('/book_details',auth="public",website=True)
    def display_book(self,book):
        domain = []
        if book:
            domain = [('id', '=', int(book))]
        book_d = request.env['library.book'].search(domain)
        return request.render('school_library.library_books_details', {
            'book': book_d,

        })

    @http.route('/author_books', auth="public", website=True)
    def filter_authors_books(self, author_id=None):
        domain = []
        if author_id:
            domain = [('author_id.id', '=', int(author_id))]

        books = request.env['library.book'].search(domain)

        return request.render('school_library.library_books_list', {
            'books': books,
            'categories': request.env['library.book.category'].search([]),
        })

