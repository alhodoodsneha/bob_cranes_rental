# -*- coding: utf-8 -*-
#############################################################################
from email.policy import default

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


class CaseType(models.Model):
    _name = 'case.type'
    _description = 'Case Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'


    name = fields.Char(
        string="Name",
        tracking=True
    )


class LegalCase(models.Model):
    _name = 'legal.case'
    _description = 'Legal Case'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence_code'

    name = fields.Html(
        string="Case Details",
        tracking=True
    )
    sequence_code = fields.Char(string="sequence", tracking=True)

    status = fields.Selection(
        [('new', 'New'), ('notified', 'Notified'),
         ('rdc_opened', 'RDC Case Opened'), ('in_court', 'In Court'),
         ('settled', 'Settled'), ('judgement', 'Judgement Issued'),
         ('execution', 'Execution')], default='new',
        string="Status", tracking=True)

    case_reference = fields.Char(string="Case Reference")
    case_register = fields.Boolean(
        string="Case Register",
        default=False
    )
    case_type = fields.Many2one(
        'case.type',
        string="Case Type"
    )
    partner_id = fields.Many2one('res.partner', string="Customer")
    reason = fields.Text(string="Reason")
    priority = fields.Selection(
        [('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')],
        string="Priority", default='1'
    )

    project_id = fields.Many2one(
        'project.project',
        string="Project"
    )

    next_action_date = fields.Date(string="Next Action Date")

    legal_notes = fields.Text(
        string="Legal Notes"
    )

    pdc_received_id = fields.Many2one(
        'pdc.payment.received',
        string="Pdc Received"
    )

    @api.model
    def create(self, vals):
        res = super(LegalCase, self).create(vals)
        res.sequence_code = self.env['ir.sequence'].next_by_code('legal.case')
        return res