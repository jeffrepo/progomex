# -*- coding: utf-8 -*-
{
    'name': "Progomex",

    'summary': """
        Generación de reportes PDF para Carta Porte en inventario y entregas.
    """,

    'description': """
        Módulo para la generación de reportes en formato PDF relacionados con la Carta Porte.
        Este módulo permite crear reportes detallados que incluyen información relevante
        sobre el inventario y las entregas, facilitando la gestión documental y el cumplimiento
        de normativas mexicanas en el transporte de mercancías.
        
        Características principales:
        - Generación de reportes PDF para Carta Porte.
        - Integración con el módulo de inventario y entregas.
        - Personalización de los detalles incluidos en el reporte.
        - Cumplimiento con normativas mexicanas.
    """,

    'author': "SISPAV",
    'website': "https://www.yourcompany.com",

    # Categorías
    'category': 'Inventory/Delivery',
    'version': '0.1',
    'license': 'LGPL-3',

    # Dependencias
    'depends': ['base', 'stock', 'delivery'],

    # Archivos de datos
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/letter_delivery_report.xml',
        'reports/report_action.xml',
    ]
}