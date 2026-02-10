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
from email.policy import default

from odoo import api, models, fields,_
from odoo.exceptions import UserError


class Lead(models.Model):
    _inherit = 'crm.lead'

    sequence_code = fields.Char(
        string="Sequence Code",
        tracking=True,
        copy=False
    )

    job_name = fields.Char(
        string="Job Name"
    )


    job_details = fields.Html(
        string="Job Details",
        copy=False
    )

    is_inspection_required = fields.Boolean(
        string="Is Inspection Required",
        default=True,
        copy=False
    )

    assigned = fields.Boolean(
        string="Assigned",
        default=False,
        copy=False
    )

    complete_inspection = fields.Boolean(
        string="Complete Inspection",
        default=False,
        copy=False
    )

    stage_type = fields.Selection(
        [('draft', 'Draft'),
         ('under_inspection', 'Under Inspection'),
         ('inspection_completed', 'Inspection Completed'),
         ('quote_created', 'Quote Created'),
         ('quote_confirmed', 'Quote Confirmed'),
         ('quote_revised', 'Quote Revised'),
         ('quote_cancelled', 'Quote Cancelled'),
         ],
        string="Stages",
        default='draft',
        copy=False
    )

    site_location = fields.Text(
        string="Site Location",
        copy=False
    )

    inspection_task = fields.Many2one(
        'project.task',
        string="Inspection Task",
        copy=False
    )

    is_quote_created = fields.Boolean(
        string="Is Quote Created",
        default=False,
    )

    @api.model
    def create(self, vals):
        """ Create function inherited for sequence generation """
        res = super(Lead, self).create(vals)
        res.sequence_code = self.env['ir.sequence'].next_by_code('crm.lead')
        return res

    def _get_lead_sale_order_domain(self):
        """Override the function to add new domain"""
        domain = super(Lead, self)._get_lead_sale_order_domain()
        domain.append(('state', '!=', 'revision'))
        return domain

    def action_assign_to_job_creation(self):
        if not self.job_name:
            raise UserError(_("Please Add the job name"))
        inspection_manager = self.env['inspection.team.member'].search([],
                                                                       limit=1)
        if not inspection_manager:
            raise UserError(_("Please Configure The Inspection Team"))
        if not self.date_deadline:
            raise UserError(_("Please Add closing date"))
        return {
            'name': 'Assign Inspection',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'inspection.assign.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'default_crm_lead_id': self.id
            }
        }

    def action_create_quotation(self):
        sale_order = self.env['sale.order'].sudo().create({
            'partner_id': self.partner_id.id,
            'opportunity_id': self.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'origin': self.name,
            'source_id': self.source_id.id,
            'company_id': self.company_id.id or self.env.company.id,
            'tag_ids': [(6, 0, self.tag_ids.ids)],
            'team_id': self.team_id.id,
            'user_id': self.user_id.id,
            'crm_lead_id': self.id,
        })
        self.stage_type = 'quote_created'
        self.is_quote_created = True
        return {
            'name': 'Quotation',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current'
        }
