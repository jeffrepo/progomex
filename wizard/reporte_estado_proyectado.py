# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
import logging
import xlsxwriter
import base64
import io
import json

class ReporteEstadoProyectado(models.TransientModel):
    _name = 'progomex.reporte_estado_proyectado'
    _description = "Reporte estado proyectado wizard"

    fecha_inicio = fields.Date("Fecha inicio")
    fecha_fin = fields.Date("Fecha fin")
    cuenta_analitica_id = fields.Many2one("account.analytic.account","Cuenta analítica")
    name = fields.Char('Nombre archivo', size=32)
    archivo = fields.Binary('Archivo', filters='.xlsx')

    def obtener_gastos_indirectos(self, fecha_inicio, fecha_fin, cuenta_analitica_id):
        gastos_indirectos = {}
        gastos_indirectos_opciones = {}
        gasto_indirecto_ids = self.env['progomex.gasto_indirecto'].search([("id",">", 0)])
        lista_gastos_ids = []
        total = 0
        if gasto_indirecto_ids:
            for gasto in gasto_indirecto_ids:
                for cuenta_gasto in gasto.cuenta_ids:
                    gastos_indirectos_opciones[cuenta_gasto.id] = gasto.name
                lista_gastos_ids += gasto.cuenta_ids.ids

            linea_analitica_ids = self.env["account.analytic.line"].search([("date",">=",fecha_inicio),("date","<=",fecha_fin),("account_id","=",cuenta_analitica_id.id),("general_account_id","in",lista_gastos_ids)])
            if linea_analitica_ids:
                for linea in linea_analitica_ids:
                    gasto = False
                    if linea.general_account_id.id in gastos_indirectos_opciones:
                        gasto = gastos_indirectos_opciones[linea.general_account_id.id]

                        if gasto not in gastos_indirectos:
                            gastos_indirectos[gasto] = 0
                        monto = linea.amount * -1
                        gastos_indirectos[gasto] += monto
                        total += monto
        return [gastos_indirectos, total]

    def obtener_inventario(self, fecha_inicio, fecha_fin):
        datos_inventario = {}
        apartado_inventario_id = self.env['progomex.inventario'].search([("id",">", 0)])
        logging.warning(apartado_inventario_id)
        if apartado_inventario_id:
            for apartado in apartado_inventario_id:
                nombre_apartado = apartado.codigo
                if nombre_apartado not in datos_inventario:
                    datos_inventario[nombre_apartado] = {"nombre": apartado.name, "total": 0}

                movimiento = False
                    
                if apartado.tipo == "inicial_deudor":
                    movimientos = self.env["account.move.line"].search([("account_id","in", apartado.cuenta_ids.ids),("date","<",fecha_inicio)])
                    for m in movimientos:
                        datos_inventario[nombre_apartado]["total"] += (m.debit - m.credit)
                elif apartado.tipo == "inicia_acreedor":
                    movimientos = self.env["account.move.line"].search([("account_id","in", apartado.cuenta_ids.ids),("date","<",fecha_inicio)])
                    for m in movimientos:
                        datos_inventario[nombre_apartado]["total"] += (m.credito - m.debit)
                elif apartado.tipo == "acumulado_deudor":
                    movimientos = self.env["account.move.line"].search([("account_id","in", apartado.cuenta_ids.ids),("date",">=", fecha_inicio),("date","<=", fecha_fin)])
                    for m in movimientos:
                        datos_inventario[nombre_apartado]["total"] += (m.debit - m.credit)
                elif apartado.tipo == "acumulado_acreedor":
                    movimientos = self.env["account.move.line"].search([("account_id","in", apartado.cuenta_ids.ids),("date",">=", fecha_inicio),("date","<=", fecha_fin)])
                    for m in movimientos:
                        datos_inventario[nombre_apartado]["total"] += (m.credit - m.debit)
                # elif apartado.tipo == "balanza_final_deudor":
                # elif apartado.tipo == "balanza_final_acreedor":
                else:
                    if apartado.codigo_py:
                        movimiento = False
    #                     logging.warning("calculado")
    #                     logging.warning(datos_inventario)
    #                     logging.warning(apartado.codigo_py)
    #                     localdict = apartado.codigo_py
    #                     datos_inventario[nombre_apartado]["total"] = safe_eval(apartado.codigo_py, json.loadslocaldict, mode="exec", nocopy=True)
    # #localdict = {'base_amount': base_amount, 'price_unit': price_unit, 'quantity': quantity, 'product': product_sudo, 'partner': partner, 'company': company}
    #safe_eval(self.python_compute, localdict, mode="exec", nocopy=True)
                        
        logging.warning(datos_inventario)
        return datos_inventario
    
    def print_report_excel(self):
        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            


            gastos_indirectos = self.obtener_gastos_indirectos(w.fecha_inicio, w.fecha_fin, w.cuenta_analitica_id)
            inventarios = self.obtener_inventario(w.fecha_inicio, w.fecha_fin)
            hoja = libro.add_worksheet('Estado proyectado')
            hoja.write(0,3,str(self.env.user.company_id.name))
            hoja.write(1,3,str(self.env.user.company_id.partner_id.contact_address_complete))
            hoja.write(2,3,"RFC: " +str(self.env.user.company_id.vat))
            hoja.write(3,3,"Estado Proyectado de Costo de Producción y Venta Jose Azueta")
            hoja.write(4,4,"02/28/2025")


            # hoja.write(6,0, 'Inventario Inicial de Producción en Proceso')
            # hoja.write(7,0, 'Inventario Inicial de Materia Prima')
            # hoja.write(8,0, 'compras de materia prima ')
            # hoja.write(9,0, 'Gastos de compra de materia prima')
            # hoja.write(10,0, 'disponible')
            # hoja.write(11,0, 'Inventario final de materia prima')
            # hoja.write(12,0, 'costo de la materia prima utilizada')
            # hoja.write(13,0, 'mano de obra directa')
            # hoja.write(14,0, 'costo primo')

            fila = 6
            for apartado in inventarios:
                if "nombre" in inventarios[apartado]:
                    fila += 1
                    logging.warning(inventarios[apartado])
                    hoja.write(fila, 0, inventarios[apartado]["nombre"])
                    hoja.write(fila, 1, inventarios[apartado]["total"])
                    
            fila += 2
            hoja.write(fila,0, 'Gastos Indirectos de Producción')
            for gasto in gastos_indirectos[0]:
                fila += 1
                monto = gastos_indirectos[0][gasto]
                porcentaje = (monto / gastos_indirectos[1])*100
                decimal = monto
                hoja.write(fila, 0, gasto)
                hoja.write(fila, 2, monto)
                hoja.write(fila, 3, porcentaje)

            fila += 1
            hoja.write(fila, 3, gastos_indirectos[1])

            fila += 2
            hoja.write(fila,0, 'costo incurrido')
            fila += 1
            hoja.write(fila,0, 'costo total de produccion')
            fila += 1
            hoja.write(fila,0, 'Inv.  final de produccion en proceso')
            fila += 1
            hoja.write(fila,0, 'costo total de produccion terminada')
            fila += 1
            hoja.write(fila,0, 'Inv. inicial de producto terminado')
            fila += 1
            hoja.write(fila,0, 'Inv. final de producto terminado')
            fila += 1
            hoja.write(fila,0, 'costo de ventas')
            fila += 1

            
            
            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo':datos, 'name':'reporte_estado_proyectado.xlsx'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'progomex.reporte_estado_proyectado',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

