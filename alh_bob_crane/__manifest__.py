# -*- coding: utf-8 -*-
#############################################################################

#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public License
#    (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License (AGPL v3) for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'Equipment Rental Management',
    'version': '19.0.0.0.4',
    'category': 'Equipment Rental Management',
    'sequence': 2,
    'website': 'https://www.alhodood.com/',
    'author': 'Alhodood Technologies',
    'summary': 'Equipment Rental Management',
    'description': 'Equipment Rental Mangement For Uae ',
    'depends': ['sale_management', 'account', 'project', 'analytic', 'stock','hr_timesheet',
                'crm', 'sale_crm','utm','documents','mail','sale_project','hr','pdc_payment_property',
                'account_analytic_parent','account_asset_fleet','project_task_risk_management_odoo',
                'project_task_default_stage'
                ],
    'data': [
        'data/ir_sequence.xml',
        'data/mail_templates.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/inspection_team.xml',
        'views/fleet_vehicle.xml',
        'views/hse_checklist.xml',
        'views/crm_lead.xml',
        'views/project_project.xml',
        'views/inspectionl_report_template.xml',
        'views/report_timesheet_template.xml',
        'views/ir_action_report.xml',
        'views/project_task.xml',
        'views/sale_order.xml',
        'views/work_timesheet.xml',
        'views/legal_case.xml',
        'views/legal_team.xml',
        'views/document_document.xml',
        'views/pdc_payment_received.xml',
        'wizard/job_card_adding_wizard.xml',
        'wizard/inspection_task_assign_wizard.xml',
        'wizard/project_task_assign_wizard.xml',
        'wizard/lpo_adding_wizard.xml',
        'wizard/hse_check_list_wizard.xml',
        'wizard/loading_equipments_wizard.xml',
        'wizard/timesheet_print_wizard.xml',
    ],
    'demo': [
    ],
    'assets': {

    },
    'external_dependencies': {

    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
