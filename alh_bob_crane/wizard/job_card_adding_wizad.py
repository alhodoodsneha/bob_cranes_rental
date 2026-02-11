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


class JobCardAddingWizard(models.TransientModel):
    _name = 'job.card.adding.wizard'
    _description = "Job Card Creation"

    sale_order = fields.Many2one(
        'sale.order',
        string="Sale Order",
    )

    user_id = fields.Many2one(
        'res.users',
        domain=lambda self: [('group_ids', 'in', self.env.ref(
            'alh_bob_crane.group_project_manaager_admin').id)],
        string="Project Manager"
    )

    def action_assign_to(self):
        project = self.env['project.project'].sudo().create(
            {
                'name':self.sale_order.crm_lead_id.job_name,
                'user_id':self.user_id.id,
                'partner_id':self.sale_order.partner_id.id,
                'company_id':self.sale_order.company_id.id,
                'sale_order_job':self.sale_order.id,
                'crm_lead_id':self.sale_order.crm_lead_id.id,
                'project_value':self.sale_order.amount_total,
                'is_job_work':True,
            }
        )
        if self.sale_order.crm_lead_id.inspection_task:
            self.sale_order.crm_lead_id.inspection_task.sudo().write({
                'project_id': project.id
            })
        self.sale_order.create_job = True
        self.sale_order.job_project_id = project.id
