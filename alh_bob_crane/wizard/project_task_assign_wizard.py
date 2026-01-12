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


class ProjectTaskAssignWizard(models.TransientModel):
    _name = 'project.assign.wizard'
    _description = "Project Assign To"

    assign_to = fields.Many2many(
        'res.users',
        'assign_to',
        string='Assign To',
        domain=lambda self: [('group_ids', 'in', [
                    self.env.ref('alh_bob_crane.group_inspection_user').id,
                    self.env.ref('alh_bob_crane.group_inspection_manager').id,
                ])]
    )

    def action_assign_to(self):
        project_task = self.env['project.task'].browse(self.env.context['active_id'])
        project_task.write({'user_ids': [(6, 0, self.assign_to.ids)]})



class ProjectTaskHSEAssignWizard(models.TransientModel):
    _name = 'project.assign.hse.wizard'
    _description = "HSE Assign To"

    assign_to = fields.Many2many(
        'res.users',
        'project_assign_hse_wizard_rel',
        'hse__id',
        'hse_user_id',
        string='Assign To',
        domain=lambda self: [
            ('group_ids', 'in', [
                self.env.ref('alh_bob_crane.group_hse_group_manager').id,
                self.env.ref('alh_bob_crane.group_hse_user').id,
            ])
        ]
    )

    def action_assign_to(self):
        project_task = self.env['project.task'].browse(self.env.context['active_id'])
        project_task.write({'user_ids': [(6, 0, self.assign_to.ids)]})


class ProjectTaskTransportationAssignWizard(models.TransientModel):
    _name = 'project.assign.transportation.wizard'
    _description = "Transportation Assign To"

    assign_to = fields.Many2many(
        'res.users',
        'project_assign_transportation_wizard_rel',
        'transportation__id',
        'transportation_user_id',
        string='Assign To',
        domain=lambda self: [
            ('group_ids', 'in', [
                self.env.ref('alh_bob_crane.group_transport_group_manager').id,
                self.env.ref('alh_bob_crane.group_transport_user').id,
            ])
        ]
    )

    def action_assign_to(self):
        project_task = self.env['project.task'].browse(self.env.context['active_id'])
        project_task.write({'user_ids': [(6, 0, self.assign_to.ids)]})


class ProjectTaskLoadingAssignWizard(models.TransientModel):
    _name = 'project.assign.loading.wizard'
    _description = "Loading Task Assign To"

    assign_to = fields.Many2many(
        'res.users',
        'project_assign_loading_wizard_rel',
        'loading__id',
        'loading_user_id',
        string='Assign To',
        domain=lambda self: [
            ('group_ids', 'in', [
                self.env.ref('alh_bob_crane.group_loading_group_manager').id,
                self.env.ref('alh_bob_crane.group_loading_user').id,
            ])
        ]
    )

    def action_assign_to(self):
        project_task = self.env['project.task'].browse(self.env.context['active_id'])
        project_task.write({'user_ids': [(6, 0, self.assign_to.ids)]})