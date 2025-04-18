# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProgomexGastosIndirectos(models.Model):
    _name = 'progomex.gasto_indirecto'
    _order = 'sequence'
    
    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Char("Nombre")
    cuenta_ids = fields.Many2many("account.account",string="Cuenta")

class ProgomexGastosAdministrativo(models.Model):
    _name = 'progomex.gasto_administrativo'
    _order = 'sequence'
    
    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Char("Nombre")
    cuenta_ids = fields.Many2many("account.account",string="Cuenta")