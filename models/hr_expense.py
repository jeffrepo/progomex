# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    departamento_id = fields.Many2one('hr.department', string='Departamento')