# -*- coding: utf-8 -*-
# from odoo import http


# class TechnicalAssessment(http.Controller):
#     @http.route('/technical_assessment/technical_assessment', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/technical_assessment/technical_assessment/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('technical_assessment.listing', {
#             'root': '/technical_assessment/technical_assessment',
#             'objects': http.request.env['technical_assessment.technical_assessment'].search([]),
#         })

#     @http.route('/technical_assessment/technical_assessment/objects/<model("technical_assessment.technical_assessment"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('technical_assessment.object', {
#             'object': obj
#         })

