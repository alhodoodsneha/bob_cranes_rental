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
from odoo import api, models, fields,_


class HseChecklist(models.Model):
    _name = 'hse.checklist'
    _description = 'Hse Checklist'
    _rec_name = 'name'

    name = fields.Char(
        string="Name",
        tracking=True
    )

    checklists_line_ids = fields.One2many(
        'hse.checklist.line',
        'checkist_id',
        string="Check List Line"
    )

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        readonly=True
    )


class HseChecklistLine(models.Model):
    _name = 'hse.checklist.line'
    _description = 'Hse Checklist Items'
    _rec_name = 'name'

    checkist_id = fields.Many2one(
        'hse.checklist',
        string="Checklist",
    )

    name = fields.Char(
        string="Checklist",
        tracking=True
    )
