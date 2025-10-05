# -*- coding: utf-8 -*-
# from odoo import http


# class Training20(http.Controller):
#     @http.route('/training20/training20', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/training20/training20/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('training20.listing', {
#             'root': '/training20/training20',
#             'objects': http.request.env['training20.training20'].search([]),
#         })

#     @http.route('/training20/training20/objects/<model("training20.training20"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('training20.object', {
#             'object': obj
#         })

