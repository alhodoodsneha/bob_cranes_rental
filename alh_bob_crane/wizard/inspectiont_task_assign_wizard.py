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
from odoo import api, models, fields
from odoo.exceptions import UserError


class InspectionTaskAssignWizard(models.TransientModel):
    _name = 'inspection.assign.wizard'
    _description = "Inspection Assign To"

    crm_lead_id = fields.Many2one(
        'crm.lead',
        string="Crm Lead"
    )

    deadline = fields.Datetime(
        string="DeadLine"
    )

    def action_assign_to(self):
        inspection_manager = self.env['inspection.team.member'].search([],
                                                                       limit=1)
        is_internal_pr = self.env['project.project'].sudo().search(
            [('inspection_project','=',True),
             ('company_id','=',self.crm_lead_id.company_id.id)]
        )
        if not is_internal_pr:
            admin_user = self.env.ref("base.user_admin")
            if not admin_user:
                raise UserError("Admin Not Found")
            is_internal_pr = self.env['project.project'].sudo().create({
                'name': "Inspection Project",
                'user_id': admin_user.id,
                'allow_timesheets': True,
                'inspection_project': True,
                'date_start': fields.Date.today(),
                'company_id':self.crm_lead_id.company_id.id,
                'privacy_visibility': 'followers'
            })
        sequence_insp_task = self.env['ir.sequence'].next_by_code(
            'project.task.inspection')
        project_task = self.env['project.task'].sudo().create({
            'name': str(sequence_insp_task) + '-' + self.crm_lead_id.job_name,
            'user_ids': [(6, 0, [inspection_manager.team_manager_id.id])],
            'partner_id': self.crm_lead_id.partner_id.id,
            'description': self.crm_lead_id.job_details,
            'project_id': is_internal_pr.id,
            '_is_inspection_task': True,
            'date_deadline': self.deadline,
            'crm_lead_id': self.crm_lead_id.id,
            'site_location': self.crm_lead_id.site_location,
        })
        self.crm_lead_id.write({
            'assigned': True,
            'stage_type': 'under_inspection',
            'inspection_task': project_task.id,
        })
