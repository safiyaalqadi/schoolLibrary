from odoo import http,api
from odoo.http import request

class studentController(http.Controller):

    @http.route('/students',auth='public',website=True)
    def display_students(self):
        students=request.env['library.students'].sudo().search([])
        students2=[]
        return request.render('school_library.library_students_list',{
            'students':students
        })

    @http.route('/top_students', auth='public', website=True)
    def display_top_students(self):

        students = request.env['library.students'].sudo().search([], limit=10,
                                                                 order='rank desc')
        return request.render('school_library.library_students_list', {
            'students': students
        })