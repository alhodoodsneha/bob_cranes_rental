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


class LoadingEquipmentWizard(models.TransientModel):
    _name = 'loading.equipment.wizard'
    _description = "Loading Equipments"

    project_id = fields.Many2one(
        'project.project',
        string="Project"
    )

    task_id = fields.Many2one(
        'project.task',
        string="Task"
    )

    type_load = fields.Selection(
        [('loading','Loading'),
         ('unloading','Unloading'),
         ('installing','Installing')],
        string="Type"
    )

    allowed_equipment_ids = fields.Many2many(
        'equipment.allocation',
        string="Allowed Equipments",
        compute='_compute_allowed_equipments'
    )

    equipment_ids = fields.Many2many(
        'equipment.allocation',
        string="Equipments",
        domain="[('id','in',allowed_equipment_ids)]"
    )

    @api.depends('type_load', 'project_id','task_id')
    def _compute_allowed_equipments(self):
        """Compute allowed equipments based on type_load and project."""
        status_map = {
            'loading': 'waiting',
            'installing': 'loading',
            'unloading': 'installed',
        }
        for wizard in self:
            status = status_map.get(wizard.type_load)
            if status:
                domain = [('loading_status', '=', status)]
                if wizard.project_id:
                    domain.append(('project_id', '=', wizard.project_id.id))
                wizard.allowed_equipment_ids = self.env[
                    'equipment.allocation'].search(domain)
            else:
                wizard.allowed_equipment_ids = self.env[
                    'equipment.allocation'].browse([])

    def action_assign_to(self):
        if not self.type_load:
            raise UserError("Please Choose The type !!")
        if not self.equipment_ids:
            raise UserError("Please Choose The Equipments !!")
        if not self.project_id.project_loc.sudo().id:
            raise UserError("Please Choose The Project Location !!")
        for rec in self.equipment_ids:
            if self.type_load == 'loading':
                rec.loading_status = 'loading'
                load = self.env['equipment.loading.task'].create({
                    'task_id': self.task_id.id,
                    'project_id': self.project_id.id,
                    'equipment_allocation_id': rec.id,
                    'updated_by': self.env.user.id,
                    'updated_on':fields.Date.today(),
                    'status_updated': "Loading Done"
                })
            elif self.type_load == 'unloading':
                rec.loading_status = 'unload'
                load =self.env['equipment.loading.task'].create({
                    'task_id': self.task_id.id,
                    'project_id': self.project_id.id,
                    'equipment_allocation_id': rec.id,
                    'updated_by': self.env.user.id,
                    'updated_on': fields.Date.today(),
                     'status_updated': "Unloading Done"
                })
            else:
                rec.loading_status = 'installed'
                load = self.env['equipment.loading.task'].create({
                    'task_id': self.task_id.id,
                    'project_id': self.project_id.id,
                    'equipment_allocation_id': rec.id,
                    'updated_by': self.env.user.id,
                    'updated_on': fields.Date.today(),
                     'status_updated': "Installation Completed"
                })
            self.env['fleet.vehicle.location.history'].sudo().create({
                'vehicle_id':rec.equipment_id.id,
                'source_location_id':rec.equipment_id.project_loc.sudo().id,
                'destination_location_id':self.project_id.project_loc.sudo().id,
            })
            rec.equipment_id.project_loc = self.project_id.project_loc.id