from odoo import models, fields, api
from datetime import datetime, timedelta


class LibraryBookReturnReport(models.TransientModel):
    _name = 'library.book.return.report'
    _description = 'Library Book Return Report'

    start_date = fields.Date(string="Start Date", default=fields.Date.context_today)
    end_date = fields.Date(string="End Date", default=fields.Date.context_today)

    @api.model
    def get_books_not_returned_in_week(self):
        today = fields.Date.context_today(self)
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        orders = self.env['library.book.order'].search([
            ('order_date', '>=', start_of_week),
            ('order_date', '<=', end_of_week),
            ('status', '=', 'borrowed'),
            ('return_date', '=', False)
        ])

        return orders
