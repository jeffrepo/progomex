# -*- coding: utf-8 -*-
# from odoo import http


# class L10nMxProgomex(http.Controller):
#     @http.route('/l10n_mx_progomex/l10n_mx_progomex', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_mx_progomex/l10n_mx_progomex/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_mx_progomex.listing', {
#             'root': '/l10n_mx_progomex/l10n_mx_progomex',
#             'objects': http.request.env['l10n_mx_progomex.l10n_mx_progomex'].search([]),
#         })

#     @http.route('/l10n_mx_progomex/l10n_mx_progomex/objects/<model("l10n_mx_progomex.l10n_mx_progomex"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_mx_progomex.object', {
#             'object': obj
#         })

