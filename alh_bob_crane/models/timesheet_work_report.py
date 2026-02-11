# -*- coding: utf-8 -*-
#############################################################################
#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public License (AGPL v3), Version 3.
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
from odoo import models, api

class ReportTimesheetWork(models.AbstractModel):
    _name = 'report.alh_bob_crane.report_timesheet_worked_report'
    _description = 'Timesheet Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        project_id = data.get('project_id')
        total_amount = 0.0
        lines = self.env['work.timesheet.line'].search([
            ('project_id', '=', int(project_id)),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
        ], order="date asc")
        total_amount = sum(lines.mapped('total_hours'))
        return {
            'doc_ids': lines.ids,
            'doc_model': 'work.timesheet.line',
            'docs': lines,
            'company': self.env.company,
            'project_id': data.get('project') if data else False,
            'start_date': data.get('start_date') if data else False,
            'end_date': data.get('end_date') if data else False,
            'total_amount': total_amount,
        }
