# -*- coding: utf-8 -*-
#############################################################################

#    Alhodood Technologies.
#
#    Copyright (C) 2026-TODAY Alhodood Technologies(<https://www.alhodood.com>)
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
    'name': 'Dashboards',
    'version': '19.0.0.0.4',
    'category': 'Equipment Rental Management',
    'sequence': 2,
    'website': 'https://www.alhodood.com/',
    'author': 'Alhodood Technologies',
    'summary': 'Equipment Rental Management',
    'description': 'Dashboards',
    'depends': ['spreadsheet_dashboard','alh_bob_crane'
                ],
    'data': [
        'security/res_group.xml',
        'views/menu_items.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'alh_dashboards/static/src/js/chart.js',
            'alh_dashboards/static/src/js/project_dashboard.js',
            'alh_dashboards/static/src/js/equipment_dashboard.js',
            'alh_dashboards/static/src/xml/project_dashboard.xml',
            'alh_dashboards/static/src/xml/equipment_dashboard.xml',
        ],
    },
    'external_dependencies': {

    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
