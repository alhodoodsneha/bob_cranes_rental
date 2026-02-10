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
from odoo.exceptions import UserError

class WorkTimesheet(models.Model):
    _name = 'work.timesheet'
    _description = 'Work Timesheet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'project_id'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        tracking=True
    )

    state = fields.Selection(
        [
            ('draft', 'Prepared'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
        ],
        string='Status',
        default='draft',
        tracking=True
    )

    line_ids = fields.One2many(
        'work.timesheet.line',
        'timesheet_id',
        string='Timesheet Lines'
    )

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        readonly=True
    )

    def action_submit(self):
        if not self.line_ids:
            raise UserError(_("Please Add Timesheet Lines"))
        self.write({'state': 'submitted'})

    def action_approve(self):
        for line in self.line_ids:
            self.env['account.analytic.line'].create({
                'name': line.name,
                'date': line.date,
                'employee_id': line.employee_id.id,
                'project_id': line.project_id.id,
                'unit_amount': line.hours,
                'company_id': self.company_id.id,
            })
        self.write({'state': 'approved'})
        groups = [
            'alh_bob_crane.group_project_manaager_admin',
            'alh_bob_crane.group_timesheet_collection',
        ]
        users = self.env['res.users'].sudo().search([
            ('group_ids', 'in', [
                self.env.ref(group).id for group in groups
            ])
        ])
        cc_emails = ','.join(
            email for email in users.mapped('partner_id.email') if email
        )
        if self.project_id.user_id.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            body_html = f"""
                                <p>Dear {self.project_id.user_id.name},</p>
                                    <p>
                                    We are pleased to inform you that the timesheet has been reviewed and approved by the client.
                                    </p>
                                    All reported working hours have been verified and accepted as per the agreed scope and timeline. You may proceed with the next steps as required.

                                           <p>
                                           Please let us know if any further clarification or action is needed.
                                             </p>
                                             <p>
                                            Thank you for your cooperation and support.
                                             </p>

                                             <p>
                                                <a href="{record_url}"
                                                   style="
                                                       background-color:#0a6ebd;
                                                       color:#ffffff;
                                                       padding:8px 14px;
                                                       text-decoration:none;
                                                       border-radius:4px;
                                                       display:inline-block;
                                                   ">
                                                   View Work Timehseet
                                                </a>
                                            </p>
                                            <p>
                                                Best regards,<br/>
                                                {self.env.user.name}
                                            </p>
                                    """
            subject = _(
                'Timesheet Approved by Client - %s') % (
                          self.project_id.name)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.project_id.user_id.partner_id.email,
                'email_cc': cc_emails,
            }
            self.env['mail.mail'].sudo().create(main_content).send()



class WorkTimesheetLine(models.Model):
    _name = 'work.timesheet.line'
    _description = 'Work Timesheet Line'
    _rec_name = 'name'

    timesheet_id = fields.Many2one(
        'work.timesheet',
        ondelete='cascade'
    )

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        related='timesheet_id.project_id',
        tracking=True,
    )

    task_id = fields.Many2one(
        'project.task',
        string="Task",
        domain="[('project_id','=',project_id)]"
    )

    name = fields.Char(
        string="Description"
    )
    date = fields.Date(
        required=True
    )

    allowed_employee_ids = fields.Many2many(
        'hr.employee',
        compute='_compute_allowed_employees',
        store=False
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        domain="[('id', 'in', allowed_employee_ids)]"
    )

    employee_badge = fields.Char(
        string='Employee Badge',
        related='employee_id.barcode'
    )

    hours = fields.Float(
        string='Hours',
        required=True
    )


    @api.depends('timesheet_id')
    def _compute_allowed_employees(self):
        for rec in self:
            if rec.timesheet_id.project_id:
                allocations = self.env['manpower.allocation'].search([
                    ('project_id', '=', rec.timesheet_id.project_id.id)
                ])
                rec.allowed_employee_ids = allocations.mapped('employee_id')
            else:
                rec.allowed_employee_ids = False