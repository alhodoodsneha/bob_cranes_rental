# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, fields


class RiskIncident(models.TransientModel):
    """ Transient model for wizard """
    _name = 'risk.incident.simplified'

    risk_incident = fields.Char(string='Risk Incident', required=True, help='Risk Incident')
    note = fields.Text(string='Description', required=True, help='Note for Risk Incident')
    user_id = fields.Many2one('res.users', string='Assigned to', help='Select User ')
    project_id = fields.Many2one('project.project', string='Project', help='Select Project ')
    task_id = fields.Many2one('project.task',string="Task")
    image = fields.Binary(string='Incident Photo', help='Image')

    def create_incident(self):
        """ Creating Risk Incident Through Wizard """
        self.env['risk.incident'].create({
            'risk_incident': self.risk_incident,
            'user_id': self.user_id.id,
            'task_id': self.task_id.id,
            'crm_lead_id': self.task_id.crm_lead_id.sudo().id,
            'incident_image': self.image,
            'note': self.note
        })
