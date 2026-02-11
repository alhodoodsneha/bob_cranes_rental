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
from odoo import models, fields, api

class TimesheetReportWizard(models.TransientModel):
    _name = 'timesheet.report.wizard'
    _description = 'Timesheet Report Wizard'

    project_id = fields.Many2one('project.project', string="Project")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    def print_timesheet_report(self):
        lines = self.env['work.timesheet.line'].search([
            ('project_id', '=', self.project_id.id),
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date)
        ])
        total_amount = sum(lines.mapped('total_hours'))
        datas = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'project': self.project_id.name,
            'project_id': self.project_id.id,
            'total_amount': total_amount,
        }
        return self.env.ref('alh_bob_crane.action_report_timesheet').report_action(lines,data=datas)
