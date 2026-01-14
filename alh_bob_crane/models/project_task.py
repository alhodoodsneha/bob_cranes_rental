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
import base64
from odoo import api, models, fields,_
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    _is_inspection_task = fields.Boolean(
        string="IS Inspection Task",
        default=False,
        copy=False
    )

    _is_hse_task = fields.Boolean(
        string="IS Hse Task",
        default=False,
        copy=False
    )

    _is_transportation_task = fields.Boolean(
        string="IS Transportation Task",
        default=False,
        copy=False
    )

    is_completed_loading = fields.Boolean(
        string="IS Completed Loading Task",
        default=False,
        copy=False
    )

    _is_loading_task = fields.Boolean(
        string="IS Transportation Task",
        default=False,
        copy=False
    )

    crm_lead_id = fields.Many2one(
        'crm.lead',
        string="Enquiry",
        copy=False
    )

    site_location = fields.Text(
        string="Site Location",
        copy=False,
        tracking=True
    )

    inspection_attachment_ids = fields.One2many(
        'inspection.attachment',
        'task_id',
        string="Inspection Attachment",
        copy=False
    )

    is_completed  = fields.Boolean(
        string="Complete",
        default=False,
        copy=False
    )

    is_completed_verification = fields.Boolean(
        string="Complete Verification",
        default=False,
        copy=False
    )

    is_completed_transportation = fields.Boolean(
        string="Complete Transportation",
        default=False,
        copy=False
    )

    appropriate_equipment_capacity = fields.Text(
        string="Appropriate Equipment Capacity",
        copy=False
    )

    hse_verification_line_ids = fields.One2many(
        'hse.verification.checklist',
        'task_id',
        string="Hse Verification Lines"
    )

    equipment_loading_line_ids = fields.One2many(
        'equipment.loading.task',
        'task_id',
        string="Equipment Loading Lines"
    )

    def action_complete_inspection(self):
        self.is_completed = True
        self.state = '1_done'
        self.crm_lead_id.stage_type = 'inspection_completed'
        self.crm_lead_id.complete_inspection = True
        mail_template = self.env.ref(
            'alh_bob_crane.mail_crm_salesperson_inspection_complete',
            raise_if_not_found=False
        )
        if mail_template and self.crm_lead_id.user_id.email:
            mail_template.with_context(user_name=self.crm_lead_id.user_id.name).send_mail(
                self.id,
                email_values={
                    'email_to': self.crm_lead_id.user_id.partner_id.email,
                    'email_cc': self.create_uid.partner_id.email,
                },
                force_send=True
            )


    def action_assign_to(self):
        return {
            'name': 'Re Assign To',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'project.assign.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def action_assign_hse_to(self):
        return {
            'name': 'Re Assign To',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'project.assign.hse.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def action_assign_transport_to(self):
        return {
            'name': 'Re Assign To',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'project.assign.transportation.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def action_assign_loading_to(self):
        return {
            'name': 'Re Assign To',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'project.assign.loading.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def action_verified_hse(self):
        waiting_lines = self.hse_verification_line_ids.filtered(
            lambda l: l.state == 'waiting'
        )
        if waiting_lines:
            raise UserError(_(
                "HSE verification cannot be completed.\n"
                "Please complete verification of all HSE checklist items before verifying."
            ))
        self.is_completed_verification = True
        self.state = '1_done'
        groups = [
            'alh_bob_crane.group_loading_group_manager',
        ]
        users = self.env['res.users'].sudo().search([
            ('group_ids', 'in', [
                self.env.ref(group).id for group in groups
            ]),
            ('partner_id.email', '!=', False),
        ])
        cc_partners = users.mapped('partner_id')
        if self.create_uid and self.create_uid != self.env.user:
            if self.create_uid.partner_id.email:
                cc_partners |= self.create_uid.partner_id
        cc_emails = ','.join(cc_partners.mapped('email'))
        if self.project_id.user_id.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.project_id.id}&model={self.project_id._name}&view_type=form"
            body_html = f"""
                                    <p>Dear {self.project_id.user_id.name},</p>
                                        <p>
                                           This is to inform you that the HSE verification for the project {self.project_id.name}  has been successfully completed.
                                        </p>
                                        All required checks and verifications have been carried out in accordance with the approved HSE standards and guidelines. The activity is now closed, and the project may proceed to the next stage as planned.
    
                                               <p>
                                                      Please feel free to contact us if any clarification or additional information is required.
                                                 </p>
                                                 <p>
                                                 Thank you for your support and coordination.
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
                                                       View Project
                                                    </a>
                                                </p>
                                                <p>
                                                    Best regards,<br/>
                                                    {self.env.user.name}
                                                </p>
                                        """
            subject = _(
                'Completion of HSE Verification For Project - %s') % (
                          self.project_id.name)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.project_id.user_id.partner_id.email,
                'email_cc': cc_emails,
            }
            self.env['mail.mail'].sudo().create(main_content).send()

    def action_complete_transportation(self):
        self.is_completed_transportation = True
        self.state = '1_done'
        groups = [
            'alh_bob_crane.group_loading_group_manager',
        ]
        users = self.env['res.users'].sudo().search([
            ('group_ids', 'in', [
                self.env.ref(group).id for group in groups
            ]),
            ('partner_id.email', '!=', False),
        ])
        cc_partners = users.mapped('partner_id')
        if self.create_uid and self.create_uid != self.env.user:
            if self.create_uid.partner_id.email:
                cc_partners |= self.create_uid.partner_id
        cc_emails = ','.join(cc_partners.mapped('email'))
        if self.project_id.user_id.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.project_id.id}&model={self.project_id._name}&view_type=form"
            body_html = f"""
                                       <p>Dear {self.project_id.user_id.name},</p>
                                           <p>
                                              This is to inform you that the Transportation allocation for the project {self.project_id.name}  has been successfully completed.
                                           </p>
                                           All required transportation resources have been planned and assigned in accordance with the project requirements and schedule. The arrangements are now finalized and ready for execution as per the approved plan.

                                                  <p>
                                                                Please feel free to contact us if you need any clarification or further details.                                                    </p>
                                                    <p>
                                                    Thank you for your support and coordination.
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
                                                          View Project
                                                       </a>
                                                   </p>
                                                   <p>
                                                       Best regards,<br/>
                                                       {self.env.user.name}
                                                   </p>
                                           """
            subject = _(
                'Completion of Transportation Allocation For Project - %s') % (
                          self.project_id.name)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.project_id.user_id.partner_id.email,
                'email_cc': cc_emails,
            }
            self.env['mail.mail'].sudo().create(main_content).send()

    def action_loading_task(self):
        return {
            'name': 'Loading Equipment',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'loading.equipment.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'default_project_id': self.project_id.id,
                'default_task_id': self.id,
                'default_type_load': 'loading',
            }
        }

    def action_complete_loading(self):
        self.is_completed_loading = True
        self.state = '1_done'

class InspectionAttachment(models.Model):
    _name = 'inspection.attachment'

    description = fields.Text(
        string="Title"
    )
    images = fields.Binary(
        string="Images"
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task'
    )
    is_completed = fields.Boolean(
        string='Complete',
        default=False,
        related='task_id.is_completed'
    )

    def unlink(self):
        if self.is_completed:
            raise UserError(
                _("You do not have the access to delete records !!"))
        else:
            return super(InspectionAttachment, self).unlink()




class HseVerificationLines(models.Model):
    _name = 'hse.verification.checklist'
    _rec_name = 'name'
    _description = 'Hse Verification Lines'
    _order = 'sequence desc'

    name = fields.Char(
        string="Checklist"
    )

    sequence = fields.Integer(
        string="Sequence"
    )

    state = fields.Selection([
        ('waiting', 'Waiting'),
        ('done', 'Done'),
        ('fail', 'Fail')
    ],
        default='waiting',
        string="State"
    )
    notes = fields.Text(
        string="Notes"
    )

    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task'
    )

    def action_checklist_done(self):
        self.state = 'done'

    def action_checklist_fail(self):
        self.state = 'fail'

class EquipmentLoadingTask(models.Model):
    _name = 'equipment.loading.task'
    _description = 'Equipment Loading'
    _rec_name = 'equipment_id'

    project_id = fields.Many2one(
        'project.project',
        string="Project",store=True
    )

    task_id = fields.Many2one(
        'project.task',
        string="Task"
    )
    equipment_allocation_id = fields.Many2one(
        'equipment.allocation',
        string="Equipment allocation"
    )

    equipment_id = fields.Many2one(
        'fleet.vehicle',
        string='Equipment',
        domain="[('type_equipment_id','in',['equipment','lifting','trailers'])]",
        related='equipment_allocation_id.equipment_id'
    )

    start_date = fields.Datetime(required=True,
                                 related='equipment_allocation_id.start_date',
                                 string="Start Date")
    end_date = fields.Datetime(required=True,
                               related='equipment_allocation_id.end_date',
                               string="End Date")
    qty = fields.Float(
        string="quantity",
        related='equipment_allocation_id.qty'
    )

    status_updated = fields.Char(
        string="Staus Updated"
    )

    updated_by = fields.Many2one(
        'res.users',
        string="Updated By"
    )

    updated_on = fields.Date(
        string="Updated On"
    )