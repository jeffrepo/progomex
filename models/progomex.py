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

class ProgomexInventario(models.Model):
    _name = 'progomex.inventario'
    _order = 'sequence'
    
    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Char("Nombre")
    cuenta_ids = fields.Many2many("account.account",string="Cuenta")
    codigo = fields.Char("Codigo")
    tipo = fields.Selection([
        ('inicial_deudor', 'Saldo inicial deudor'),
        ('inicia_acreedor', 'Saldo inicial acreedor'),
        ('acumulado_deudor', 'Acumulado deudor'),
        ('acumulado_acreedor', 'Acumulado acreedor'),
        ('balanza_final_deudor', 'Balanza final deudor'),
        ('balanza_final_acreedor', 'Balanza final acreedor'),
    ], string="Tipo")
    codigo_py = fields.Text("Codigo python")