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
from odoo import models, fields, api,_

class LegalTeam(models.Model):
    _name = 'legal.team'
    _description = 'Legal Team Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Team Name", required=True, tracking=True)
    team_manager_id = fields.Many2one(
        'res.users',
        string='Legal Manager',
        domain=lambda self: [('id', 'in', self._get_group_manager_ids())]
    )
    team_member_ids = fields.Many2many(
        'res.users', string="Members",
        domain=lambda self: [('id', 'in', self._get_group_ist_user_ids())]
    )

    @api.model
    def _get_group_manager_ids(self):
        group = self.env.ref('alh_bob_crane.group_legal_manager')
        return group.user_ids.ids if group else []

    @api.model
    def _get_group_ist_user_ids(self):
        group = self.env.ref('alh_bob_crane.group_legal_user')
        return group.user_ids.ids if group else []
