# -*- coding: utf-8 -*-
# from odoo import http


# class ContractManagementSystem(http.Controller):
#     @http.route('/contract_management_system/contract_management_system', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contract_management_system/contract_management_system/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('contract_management_system.listing', {
#             'root': '/contract_management_system/contract_management_system',
#             'objects': http.request.env['contract_management_system.contract_management_system'].search([]),
#         })

#     @http.route('/contract_management_system/contract_management_system/objects/<model("contract_management_system.contract_management_system"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contract_management_system.object', {
#             'object': obj
#         })
