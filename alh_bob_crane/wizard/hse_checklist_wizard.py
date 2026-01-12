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


class HseChecklistWizard(models.TransientModel):
    _name = 'hse.checklist.wizard'
    _description = "Hse Checklist Wizard"

    project_id = fields.Many2one(
        'project.project',
        string="Project"
    )

    checklist_ids = fields.Many2many(
        'hse.checklist',
        string="Checklists"
    )

    deadline = fields.Datetime(
        string="Deadline",
    )

    def action_assign_to(self):
        checklists = []
        for rec in self.checklist_ids:
            if rec.checklists_line_ids:
                for line in rec.checklists_line_ids:
                    checklists.append((0, 0, {
                        'name': line.name,
                    }))
        task_id = self.env['project.task'].create({
            'name':'Hse-'+str(self.project_id.name),
            'user_ids':[(6, 0, [self.env.user.id])],
            'project_id':self.project_id.id,
            'crm_lead_id':self.project_id.crm_lead_id.sudo().id,
            'date_deadline':self.deadline,
            '_is_hse_task':True,
            'hse_verification_line_ids':checklists,
        })
        self.project_id.sudo().is_assign_hse = True
        return {
            'name': 'Hse Verification',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'project.task',
            'domain': [('id', '=', task_id.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id}
        }