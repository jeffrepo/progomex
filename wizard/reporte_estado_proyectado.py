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
        gastos_indirectos_codigo = {}
        gastos_indirectos_codigo_total = {}
        gastos_indirectos_opciones = {}
        gasto_indirecto_ids = self.env['progomex.conf_estado_proyectado'].search([("tipo","=", "gasto_indirecto")])
        lista_gastos_ids = []
        total = 0
        if gasto_indirecto_ids:
            for gasto in gasto_indirecto_ids:
                if gasto.codigo not in gastos_indirectos_codigo:
                    gastos_indirectos_codigo[gasto.codigo] = {"total": 0, "cuentas": gasto.cuenta_ids.ids if gasto.cuenta_ids else False, "nombre": gasto.name}
                    gastos_indirectos_codigo_total[gasto.codigo] = 0
                for cuenta_gasto in gasto.cuenta_ids:
                    gastos_indirectos_opciones[cuenta_gasto.id] = {"codigo": gasto.codigo, "nombre": gasto.name}
                lista_gastos_ids += gasto.cuenta_ids.ids

            linea_analitica_ids = self.env["account.analytic.line"].search([("date",">=",fecha_inicio),("date","<=",fecha_fin),("x_plan2_id","=",cuenta_analitica_id.id),("general_account_id","in",lista_gastos_ids)])

            if linea_analitica_ids:
                for linea in linea_analitica_ids:
                    gasto = False
                    if linea.general_account_id.id in gastos_indirectos_opciones:
                        gasto_codigo = gastos_indirectos_opciones[linea.general_account_id.id]["codigo"]

                        # if gasto_codigo not in gastos_indirectos_codigo:
                        #     gastos_indirectos[gasto_codigo] = 0
                            
                        monto = linea.amount * -1
                        gastos_indirectos_codigo[gasto_codigo]["total"] += monto
                        gastos_indirectos_codigo_total[gasto_codigo] += monto
                        total += monto

        ##apartados con codigo py, neceistamos recorrer de nuevo
        if gasto_indirecto_ids:
            for gasto in gasto_indirecto_ids:
                if gasto.codigo_py:
                    gasto_codigo = gasto.codigo
                    localdict = gastos_indirectos_codigo_total
                    logging.warning("localdict")
                    safe_eval(gasto.codigo_py, localdict, mode="exec", nocopy=True)
                    result = localdict.get('result', False)
                    gastos_indirectos_codigo[gasto_codigo]["total"] = result
                    gastos_indirectos_codigo_total[gasto_codigo] = result
                    #datos_inventario[gasto_codigo]["total"] = result
        logging.warning("fucnion")
        logging.warning(gastos_indirectos_codigo)
        return [gastos_indirectos_codigo, gastos_indirectos_codigo_total, total]

    def obtener_inventario(self, fecha_inicio, fecha_fin):
        datos_inventario = {}
        datos_inventario_nombre = {}
        apartado_inventario_id = self.env['progomex.conf_estado_proyectado'].search([("tipo","=", "inventario")])
        logging.warning(apartado_inventario_id)
        if apartado_inventario_id:
            for apartado in apartado_inventario_id:
                nombre_apartado = apartado.codigo
                apartado_n = apartado.name
                if nombre_apartado not in datos_inventario:
                    #datos_inventario[nombre_apartado] = {"nombre": apartado.name, "total": 0}
                    datos_inventario[nombre_apartado] = 0
                    datos_inventario_nombre[nombre_apartado] = {"nombre": apartado_n, "total":0}
                movimiento = False
                    
                if apartado.calculo == "inicial_deudor":
                    movimientos = self.env["account.move.line"].search([("account_id","in", apartado.cuenta_ids.ids),("date","<",fecha_inicio)])
                    for m in movimientos:
                        datos_inventario[nombre_apartado] += (m.debit - m.credit)
                elif apartado.calculo == "inicia_acreedor":
                    movimientos = self.env["account.move.line"].search([("account_id","in", apartado.cuenta_ids.ids),("date","<",fecha_inicio)])
                    for m in movimientos:
                        datos_inventario[nombre_apartado] += (m.credito - m.debit)
                elif apartado.calculo == "acumulado_deudor":
                    movimientos = self.env["account.move.line"].search([("account_id","in", apartado.cuenta_ids.ids),("date",">=", fecha_inicio),("date","<=", fecha_fin)])
                    for m in movimientos:
                        datos_inventario[nombre_apartado] += (m.debit - m.credit)
                elif apartado.tipo == "acumulado_acreedor":
                    movimientos = self.env["account.move.line"].search([("account_id","in", apartado.cuenta_ids.ids),("date",">=", fecha_inicio),("date","<=", fecha_fin)])
                    for m in movimientos:
                        datos_inventario[nombre_apartado] += (m.credit - m.debit)
                else:
                    if apartado.codigo_py:
                        localdict = datos_inventario
                        logging.warning("localdict")
                        safe_eval(apartado.codigo_py, localdict, mode="exec", nocopy=True)
                        result = localdict.get('result', False)
                        datos_inventario[nombre_apartado] = result

        logging.warning("datos_inventario")
        logging.warning(datos_inventario)
        for d in datos_inventario:
            logging.warning("las d")
            logging.warning(d)
            if d not in ["__builtins__","result"]:
                if d in datos_inventario_nombre:
                    datos_inventario_nombre[d]["total"] = datos_inventario[d]
        return [nombre_apartado,datos_inventario_nombre]


    def _obtener_final(self, dic_final):
        gasto_indirecto_ids = self.env['progomex.conf_estado_proyectado'].search([("tipo","=", "valor_final")])
        final_indirectos_codigo = {}
        #final_indirectos_codigo_total = {}
        if gasto_indirecto_ids:
            for gasto in gasto_indirecto_ids:
                if gasto.codigo not in final_indirectos_codigo:
                    final_indirectos_codigo[gasto.codigo] = {"total": 0, "nombre": gasto.name}
                    dic_final[gasto.codigo] = 0
            
            for gasto in gasto_indirecto_ids:
                if gasto.codigo_py:
                    gasto_codigo = gasto.codigo
                    localdict = dic_final
                    logging.warning("localdict")
                    safe_eval(gasto.codigo_py, localdict, mode="exec", nocopy=True)
                    result = localdict.get('result', False)
                    final_indirectos_codigo[gasto_codigo]["total"] = result
                    dic_final[gasto_codigo] = result
        return [final_indirectos_codigo,dic_final]
        
    
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

            fila = 6
            logging.warning("inventarios")
            logging.warning(inventarios)
            for apartado in inventarios[1]:
                fila += 1
                if apartado not in ["__builtins__","result"]:
                    logging.warning(apartado)
                    logging.warning(inventarios[1][apartado])
                    hoja.write(fila, 0, inventarios[1][apartado]["nombre"])
                    hoja.write(fila, 1, inventarios[1][apartado]["total"])
                    
            fila += 2
            hoja.write(fila,0, 'Gastos Indirectos de Producción')
            logging.warning("Gastos indirectos")
            logging.warning(gastos_indirectos[0])
            for gasto in gastos_indirectos[1]:
                if gasto not in ["__builtins__","result"]:
                    fila += 1
                    nombre_gasto = gastos_indirectos[0][gasto]["nombre"]
                    monto = gastos_indirectos[0][gasto]["total"]
                    logging.warning(nombre_gasto)
                    logging.warning(monto)
                    porcentaje = (monto / gastos_indirectos[2] if gastos_indirectos[2] > 0 else 0 )*100
                    hoja.write(fila, 0, nombre_gasto)
                    hoja.write(fila, 2, monto)
                #hoja.write(fila, 3, porcentaje)

            fila += 2
            #hoja.write(fila, 3, gastos_indirectos[1])
            dic_final = gastos_indirectos[1] | inventarios[1]
            apartado_final = self._obtener_final(dic_final)
            for apartado in apartado_final[0]:
                if apartado not in ["__builtins__","result"]:
                    logging.warning("apartado final")
                    logging.warning(apartado)
                    hoja.write(fila, 0, apartado_final[0][apartado]["nombre"])
                    hoja.write(fila, 3, apartado_final[0][apartado]["total"])
                    fila += 1
            fila += 2

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

