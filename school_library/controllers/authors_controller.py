from odoo import http,api
from odoo.http import request

class authorController(http.Controller):
    @http.route('/author_form', auth='public', website=True)
    def render_auth_form(self ):
        return request.render('school_library.library_author_web_form',{'error': 'Name and Biography are required.'})

    @http.route('/submit_author', auth="public", website=True)
    def save_author(self, **kwargs):
        try:
         name = kwargs.get('name')
         biography = kwargs.get('biography')

         author = request.env['library.author'].sudo().create({
            'name': name,
            'biography': biography,
          })
         return request.render('school_library.library_author_web_form',{'success':True})
        except Exception as e:
         return request.render('school_library.library_author_web_form', {'error': str(e)})

    @http.route('/authors', auth='public', website=True)
    def display_authors(self):
        authors = request.env['library.author'].sudo().search([])
        return request.render('school_library.library_authors_list', {
            'authors': authors
        })


