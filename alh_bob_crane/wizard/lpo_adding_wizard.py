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


class LpoAddingWizard(models.TransientModel):
    _name = 'lpo.adding.wizard'
    _description = "Lpo Adding"

    sale_order = fields.Many2one(
        'sale.order',
        string="Sale Order",
    )

    lpo_number = fields.Char(
        string="Lpo Number"
    )

    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Attachments")


    def action_assign_to(self):
        self.sale_order.lpo_number = self.lpo_number
        self.sale_order.lpo_attachment_ids = self.attachment_ids.ids
        self.sale_order.lpo_added = True


