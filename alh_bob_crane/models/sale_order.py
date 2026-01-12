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
from odoo import api, models, fields,_
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    crm_lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string="Enquiry",
        copy=False
    )

    state = fields.Selection(
        selection_add=[
            ('revision', 'Revision')
        ],
        copy=False
    )

    revision_count = fields.Integer(
        string="Revision Count",
        default=0,
    )

    parent_order = fields.Many2one(
        'sale.order',
        string="Parent Order",
    )

    create_job = fields.Boolean(
        string="Create Job",
        default=False,
        copy=False,
    )

    lpo_number = fields.Char(
        string="Lpo",

    )

    lpo_added = fields.Boolean(
        string="Lpo Added",
        default=False
    )

    lpo_attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Attachments")

    job_project_id = fields.Many2one(
        'project.project',
        string="Project"
    )

    def action_revision_sales_estimation(self):
        """ Revise The Quotation"""
        if self.parent_order:
            revision_count = self.revision_count + 1
            name = self.parent_order.name + ' -R' + str(
                revision_count)
            order_lines = []
            if self.order_line:
                for line in self.order_line:
                    order_lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'product_uom_qty': line.product_uom_qty,
                        'price_unit':line.price_unit,
                        'product_uom_id': line.product_uom_id.id,
                    }))
            sale_order = self.env['sale.order'].sudo().create({
                'name': name,
                'partner_id': self.partner_id.id,
                'opportunity_id': self.opportunity_id.id,
                'campaign_id': self.campaign_id.id,
                'medium_id': self.medium_id.id,
                'origin': self.origin,
                'source_id': self.source_id.id,
                'company_id': self.company_id.id or self.env.company.id,
                'tag_ids': [(6, 0, self.tag_ids.ids)],
                'team_id': self.team_id.id,
                'user_id': self.user_id.id,
                'crm_lead_id': self.crm_lead_id.id,
                'order_line': order_lines,
                'parent_order': self.parent_order.id,
                'revision_count': revision_count,
                'company_id': self.env.company.id,
            })
            self.state = 'revision'
            self.crm_lead_id.stage_type = 'quote_revised'
        else:
            revision_count = self.revision_count + 1
            name = self.name + ' -R' + str(
                revision_count)
            order_lines = []
            if self.order_line:
                for line in self.order_line:
                    order_lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'product_uom_qty': line.product_uom_qty,
                        'price_unit':line.price_unit,
                        'product_uom_id': line.product_uom_id.id,
                    }))
            sale_order = self.env['sale.order'].sudo().create({
                'name': name,
                'partner_id': self.partner_id.id,
                'opportunity_id': self.opportunity_id.id,
                'campaign_id': self.campaign_id.id,
                'medium_id': self.medium_id.id,
                'origin': self.origin,
                'source_id': self.source_id.id,
                'company_id': self.company_id.id or self.env.company.id,
                'tag_ids': [(6, 0, self.tag_ids.ids)],
                'team_id': self.team_id.id,
                'user_id': self.user_id.id,
                'crm_lead_id': self.crm_lead_id.id,
                'order_line': order_lines,
                'parent_order': self.parent_order.id,
                'revision_count': revision_count,
                'company_id': self.env.company.id,
            })
            self.state = 'revision'
            self.crm_lead_id.stage_type = 'quote_revised'

        return {
            'name': 'Quotation',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def _action_cancel(self):
        """ Cancel Opportunity status"""
        res = super(SaleOrder, self)._action_cancel()
        if self.crm_lead_id:
            self.crm_lead_id.stage_type = 'quote_cancelled'
        return res


    def action_attach_lpo(self):
        return {
            'name': 'Lpo Attach',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'lpo.adding.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'default_sale_order': self.id,
            }
        }

    def action_confirm(self):
        if self.crm_lead_id:
            self.crm_lead_id.stage_type = 'quote_confirmed'
        return super().action_confirm()


    def action_create_job_card(self):
        return {
            'name': 'Create Project',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'job.card.adding.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'default_sale_order': self.id,
            }
        }