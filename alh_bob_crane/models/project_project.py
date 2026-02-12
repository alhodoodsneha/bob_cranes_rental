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
from dateutil.relativedelta import relativedelta
from datetime import timedelta



class Project(models.Model):
    _inherit = 'project.project'

    inspection_project = fields.Boolean(
        string="Inspection Project",
        default=False,
        copy=False
    )

    sale_order_job = fields.Many2one(
        'sale.order',
        string="Sale Order",
    )

    crm_lead_id = fields.Many2one(
        'crm.lead',
        string="Crm Lead"
    )

    project_value = fields.Float(
        string="Project Value"
    )

    equipment_allocation_ids = fields.One2many(
        'equipment.allocation',
        'project_id',
        string="Equipment Allocation"
    )

    manpower_allocation_ids = fields.One2many(
        'manpower.allocation',
        'project_id',
        string="Manpower Allocation"
    )

    is_assign_hse = fields.Boolean(
        string="Assign Hse Done",
        default=False,
        copy=False
    )

    is_assign_transport = fields.Boolean(
        string="Assign Transport Done",
        default=False,
        copy=False
    )

    project_loc = fields.Many2one(
        'stock.location',
        string='Location'
    )
    is_schedule = fields.Boolean(
        string="Is Scheduled",
        default=False
    )

    start_inv_date = fields.Date(
        string="Start Date"
    )

    end_inv_date = fields.Date(
        sstring="End Date"
    )

    period = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')],
        string="Type",
        tracking=True,
    )

    fixed_schedule = fields.Boolean(
        string="Fixed",
        default=False,
        copy=False
    )

    invoice_allocation_ids = fields.One2many(
        'invoice.allocation',
        'project_id',
        string="Invoice Allocation"
    )

    date_fixed = fields.Date(
        string="Date"
    )

    amount_to_inv = fields.Float(
         string="Amount To Invoice"
     )

    description_inv = fields.Text(
        string="Description"
    )

    rental_rate_hourly = fields.Float(
        string="Rental Rate (Hourly)",
        default=0.0
    )

    rental_rate_daily = fields.Float(
        string="Rental Rate (Daily)",
        default=0.0
    )

    rental_rate_monthly = fields.Float(
        string="Rental Rate (Monthly)",
        default=0.0
    )

    rental_rate_weekly = fields.Float(
        string="Rental Rate (Weekly)",
        default=0.0
    )

    minimum_rental_hours = fields.Float(
        string="Minimum Rental Hours"
    )

    mobilization_charge = fields.Float(
        string="Mobilization Charge",
        default=0.0
    )

    demobilization_charge = fields.Float(
        string="Demobilization Charge",
        default=0.0
    )

    overtime_rate = fields.Float(
        string="Overtime Rate",
        default=0.0
    )

    operator_included = fields.Selection(
        [('yes','Yes'),('no','No')],
        string="Operator Included"
    )

    operator_cost = fields.Float(
        string="Operator Cost"
    )

    fuel_included = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Fuel Included"
    )

    is_job_work = fields.Boolean(
        string="Is JOb Work",
        default=False
    )

    @api.model
    def create(self, vals):
        res = super(Project, self).create(vals)
        if res.sale_order_job:
            location_vals = {
                'name': res.name,
                'usage': 'internal',
                'company_id': res.company_id.id,
            }
            location = self.env['stock.location'].sudo().create(location_vals)
            res.project_loc = location.id
        return res

    def action_schedule_invoice(self):
        for contract in self:
            if not contract.start_inv_date or not contract.end_inv_date:
                raise UserError("Please set both Start Date and End Date.")
            contract_lines = []
            current_date = contract.start_inv_date

            while current_date < contract.end_inv_date:
                contract_lines.append((0, 0, {
                    'date_inv': current_date,
                    'amount': contract.amount_to_inv,
                }))
                if contract.period == 'daily':
                    current_date += timedelta(days=1)
                elif contract.period == 'weekly':
                    current_date += timedelta(weeks=1)
                elif contract.period == 'monthly':
                    current_date += relativedelta(months=1)
                elif contract.period == 'yearly':
                    current_date += relativedelta(years=1)
                else:
                    break
            contract.write({
                'invoice_allocation_ids': contract_lines,
                'is_schedule': True,
            })

    def action_create_inv(self):
        today = fields.Date.today()
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': self.date_fixed,
            'invoice_line_ids': [(0, 0, {
                'name': self.description_inv,
                'quantity': 1,
                'price_unit': self.amount_to_inv,
            })],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        self.env['invoice.allocation'].sudo().create({
            'date_inv':self.date_fixed,
            'project_id':self.id,
            'amount':self.amount_to_inv,
            'invoice_id':invoice.id,
            'is_invoiced':True,
        })

    def action_open_planning(self):
        return {
            'name': 'Planning',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'project.operations.planning',
            'domain': [('project_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id}
        }

    def action_generate_hse(self):
        return {
            'name': 'Hse Verification',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'hse.checklist.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'default_project_id': self.id,
            }
        }


    def action_open_hse_task(self):
        return {
            'name': 'Hse',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'project.task',
            'domain': [('project_id', '=', self.id),('_is_hse_task','=',True)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id,
                        'default__is_hse_task':True
                        }
        }

    def action_open_loading_task(self):
        return {
            'name': 'Mobilization',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'project.task',
            'domain': [('project_id', '=', self.id),
                       ('_is_loading_task', '=', True)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id,
                        'default__is_loading_task': True
                        }
        }

    def action_open_un_loading_task(self):
        return {
            'name': 'De Mobilization',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'project.task',
            'domain': [('project_id', '=', self.id),
                       ('_is_de_mobilization__task', '=', True)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id,
                        'default__is_de_mobilization__task': True
                        }
        }

    def action_generate_transport(self):
        task_id = self.env['project.task'].create({
            'name': 'Transportation-' + str(self.name),
            'user_ids': [(6, 0, [self.env.user.id])],
            'project_id': self.id,
            'crm_lead_id': self.crm_lead_id.sudo().id,
            'date_deadline': fields.Datetime.now(),
            '_is_transportation_task': True,
        })
        self.sudo().is_assign_transport = True
        return {
            'name': 'Transportation',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'project.task',
            'domain': [('id', '=', task_id.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id,'default__is_transportation_task': True}
        }

    def action_open_transportation_task(self):
        return {
            'name': 'Transportation',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'project.task',
            'domain': [('project_id', '=', self.id),('_is_transportation_task','=',True)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id,
                        'default__is_transportation_task': True
                        }
        }

    def action_loading_equipments(self):
        task_id = self.env['project.task'].create({
            'name': 'Mobilization-' + str(self.name),
            'user_ids': [(6, 0, [self.env.user.id])],
            'project_id': self.id,
            'crm_lead_id': self.crm_lead_id.sudo().id,
            'date_deadline': fields.Datetime.now(),
            '_is_loading_task': True,
        })
        return {
            'name': 'Mobilization',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'project.task',
            'domain': [('id', '=', task_id.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id, 'default__is_loading_task': True}
        }

    def action_demobilization_equipments(self):
        task_id = self.env['project.task'].create({
            'name': 'DeMobilization-' + str(self.name),
            'user_ids': [(6, 0, [self.env.user.id])],
            'project_id': self.id,
            'crm_lead_id': self.crm_lead_id.sudo().id,
            'date_deadline': fields.Datetime.now(),
            '_is_de_mobilization__task': True,
        })
        return {
            'name': 'DeMobilization',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'project.task',
            'domain': [('id', '=', task_id.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id,
                        'default__is_de_mobilization__task': True}
        }

    def action_view_project_vehicles(self):
        self.ensure_one()
        return {
            'name': 'Project Vehicles',
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle',
            'view_mode': 'list,form',
            'domain': [('project_loc', '=', self.project_loc.id)],
            'context': {'default_project_loc': self.project_loc.id},
        }

class InvoiceAllocation(models.Model):
    _name = 'invoice.allocation'
    _description = 'Invoice Allocation'
    _rec_name = 'date_inv'

    date_inv = fields.Date(
        string="Invoice Date"
    )

    project_id = fields.Many2one(
        'project.project',
        string="Project"
    )

    amount = fields.Float(
        string="Amount"
    )

    invoice_id = fields.Many2one(
        'account.move',
        string="Invoice",
    )

    is_invoiced = fields.Boolean(string="Invoiced", default=False)
    invoice_status = fields.Selection(
        string="Payment Status",
        related="invoice_id.payment_state"
    )
    invoice_state = fields.Selection(
        string="Invoice Status",
        related="invoice_id.state"
    )


    def action_invoice_create(self):
        today = fields.Date.today()
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.project_id.partner_id.id,
            'invoice_date': today,
            'invoice_line_ids': [(0, 0, {
                'name': f"Rental Invoice - {self.project_id.name}",
                'quantity': 1,
                'price_unit': self.amount,
            })],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        self.invoice_id = invoice.id
        self.is_invoiced = True




class EquipmentAllocation(models.Model):
    _name = 'equipment.allocation'
    _description = 'Equipment Allocation'
    _rec_name = 'equipment_id'

    project_id = fields.Many2one(
        'project.project',
        string="Project",store=True
    )

    equipment_id = fields.Many2one(
        'fleet.vehicle',
        string='Equipment',
        domain="[('type_equipment_id','in',['equipment','lifting','trailers'])]"
    )
    start_date = fields.Datetime(required=True,
                                 string="Start Date")
    end_date = fields.Datetime(required=True,
                               string="End Date")
    qty = fields.Float(
        string="quantity"
    )

    loading_status = fields.Selection(
        [('waiting','Waiting'),
         ('loading','Loading Completed'),
         ('installed','Installed'),
         ('unload','Unload')],
        string="Status",
        default='waiting',
    )

    is_loading = fields.Boolean(
        string="Loading",
        default=False
    )
    is_installed = fields.Boolean(
        string="Installed",
        default=False
    )
    is_unloaded = fields.Boolean(
        string="Unloaded",
        default=False
    )

    rent_per_day = fields.Float(
        string="Agreed Rent Per day",
        default=0.0
    )

    as_of_today = fields.Float(
        string="As Of Today",
        compute='_compute_as_of_today'
    )

    @api.onchange('equipment_id')
    def _on_change_equipment_id(self):
        if self.equipment_id.rent_per_day:
            self.rent_per_day = self.equipment_id.rent_per_day


    @api.depends('start_date','end_date','rent_per_day','project_id')
    def _compute_as_of_today(self):
        for rec in self:
            rec.as_of_today = 0.0
            if not rec.start_date:
                continue
            start_date = rec.start_date.date()
            today = fields.Date.today()
            if rec.end_date and rec.end_date.date() < today:
                calculation_end = rec.end_date.date()
            else:
                calculation_end = today
            if start_date <= calculation_end:
                days = (calculation_end - start_date).days + 1
                rec.as_of_today = days * rec.rent_per_day

    @api.constrains('equipment_id', 'start_date', 'end_date')
    def _check_equipment_overlap(self):
        for rec in self:
            if not rec.equipment_id or not rec.start_date or not rec.end_date:
                continue

            conflict = self.search([
                ('id', '!=', rec.id),
                ('equipment_id', '=', rec.equipment_id.id),
                ('start_date', '<=', rec.end_date),
                ('end_date', '>=', rec.start_date),
            ], limit=1)

            if conflict:
                raise UserError(_(
                    "Equipment '%s' is already allocated to project '%s'\n"
                    "from %s to %s.\n\n"
                    "Please choose another date or equipment."
                ) % (
                                    rec.equipment_id.display_name,
                                    conflict.project_id.display_name,
                                    conflict.start_date,
                                    conflict.end_date
                                ))

    def unlink(self):
        for record in self:
            if record.loading_status != 'waiting':
                raise UserError(
                    _("You Can't delete line , equipment is already loaded !!"))
            return super(EquipmentAllocation, self).unlink()

class ManpowerAllocation(models.Model):
    _name = 'manpower.allocation'
    _description = 'Manpower Allocation'
    _rec_name = 'employee_id'

    project_id = fields.Many2one(
        'project.project',
         store=True,
        string="Project"
    )

    job_id = fields.Many2one('hr.job',
                             string="Job Position",
                             required=True)

    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        domain="[('job_id','=',job_id)]"
    )

    start_date = fields.Datetime(required=True,string="Start Date")
    end_date = fields.Datetime(required=True,string="End Date")
    qty = fields.Float(
        string="quantity"
    )

    @api.constrains('employee_id', 'start_date', 'end_date')
    def _check_employee_overlap(self):
        for rec in self:
            if not rec.employee_id or not rec.start_date or not rec.end_date:
                continue

            conflict = self.search([
                ('id', '!=', rec.id),
                ('employee_id', '=', rec.employee_id.id),
                ('start_date', '<=', rec.end_date),
                ('end_date', '>=', rec.start_date),
            ], limit=1)

            if conflict:
                raise UserError(_(
                    "Employee '%s' is already allocated to project '%s'\n"
                    "from %s to %s.\n\n"
                    "Please adjust the allocation dates."
                ) % (
                                    rec.employee_id.name,
                                    conflict.project_id.display_name,
                                    conflict.start_date,
                                    conflict.end_date
                                ))



class ProjectOperationsPlanning(models.Model):
    _name = 'project.operations.planning'
    _description = 'Project Operations Planning'
    _rec_name = 'name'

    name = fields.Char(default='Operations Planning',required=True)
    project_id = fields.Many2one('project.project',string="Project", required=True)
    user_id = fields.Many2one(
        'res.users',
        string="Created By",
        default=lambda self: self.env.user,
    )
    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True)

    equipment_line_ids = fields.One2many(
        'project.operations.equipment.line', 'planning_id'
    )
    manpower_line_ids = fields.One2many(
        'project.operations.manpower.line', 'planning_id'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Completed')
    ], default='draft')

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.start_date = self.project_id.date_start
            self.end_date = self.project_id.date


    def action_in_progress(self):
        self.state = 'confirmed'

    def action_completed(self):
        self.state = 'done'
        groups = [
            'alh_bob_crane.group_hse_group_manager',
            'alh_bob_crane.group_transport_group_manager',
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
                                This is to inform you that the planning for the project related to equipment and manpower allocation has been successfully completed.
                            </p>
                                  All required resources have been reviewed and scheduled in line with the project requirements and timelines. The plan is now ready for execution as per the approved schedule.

                                   <p>
                                           Please feel free to reach out if you require any clarification or further details.
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
                                           View Planning
                                        </a>
                                    </p>
                                    <p>
                                        Best regards,<br/>
                                        {self.env.user.name}
                                    </p>
                            """
            subject = _('Completion of Project Planning – Equipment and Manpower - %s') % (
                self.name)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.project_id.user_id.partner_id.email,
                'email_cc': cc_emails,
            }
            self.env['mail.mail'].sudo().create(main_content).send()


class ProjectOperationsEquipmentLine(models.Model):
    _name = 'project.operations.equipment.line'
    _description = 'Equipment Planning Line'
    _rec_name = 'equipment_id'

    planning_id = fields.Many2one(
        'project.operations.planning', required=True
    )

    project_id = fields.Many2one(
        related='planning_id.project_id', store=True,string="Project"
    )

    equipment_id = fields.Many2one(
        'fleet.vehicle',
        string='Equipment',
        domain="[('type_equipment_id','in',['equipment','lifting','trailers'])]"
    )
    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True)
    qty = fields.Float(
        string="quantity"
    )


class ProjectOperationsManpowerLine(models.Model):
    _name = 'project.operations.manpower.line'
    _description = 'Manpower Planning Line'
    _rec_name = 'job_id'

    planning_id = fields.Many2one(
        'project.operations.planning', required=True
    )
    project_id = fields.Many2one(
        related='planning_id.project_id', store=True,
        string="Project"
    )

    job_id = fields.Many2one('hr.job',
                                  string="Job Position",
                                  required=True)

    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True)
    qty = fields.Float(
        string="quantity"
    )