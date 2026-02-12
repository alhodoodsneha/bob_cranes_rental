# -*- coding: utf-8 -*-
#############################################################################

#    Alhodood Technologies.
#
#    Copyright (C) 2026-TODAY Alhodood Technologies(<https://www.alhodood.com>)
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
from odoo import models, api, fields
from datetime import date
from collections import defaultdict

class ProjectDashboard(models.Model):
    _name = "project.dashboard"
    _description = "Project Dashboard Helper"


    """Active Projects Dashboard"""

    @api.model
    def get_dashboard_data(self):

        projects = self.env['project.project'].sudo().search([('inspection_project','=',False)])

        return {
            'kpis': self._get_kpis(projects),
            'projects': self._get_projects(projects),
            'status_chart': self._get_status_chart(projects),
            'manager_chart': self._get_projects_per_manager_chart(projects),
        }

    def _get_projects(self, projects):
        dashboard_data = []

        today = date.today()

        for project in projects:

            # Tasks
            tasks = self.env['project.task'].sudo().search([
                ('project_id', '=', project.id)
            ])

            done = len(tasks.filtered(lambda t: t.state=='1_done'))
            progress = len(tasks.filtered(lambda t: t.state=='01_in_progress'))
            total_tasks = len(tasks)

            # Completion %
            completion = 0
            if total_tasks:
                completion = round(
                    ((done * 1) + (progress * 0.5)) / total_tasks * 100,
                    2
                )

            # Financial (Invoices linked via analytic account)
            invoiced = 0
            invoice_due = 0

            if project.account_id:
                invoiced = sum(project.invoice_allocation_ids.filtered(
                    lambda inv: inv.is_invoiced == True
                ).mapped('amount'))

                invoice_due = sum(project.invoice_allocation_ids.filtered(
                    lambda inv: inv.is_invoiced == False
                ).mapped('amount'))

            project_value = project.project_value or 0

            # Timeline %
            timeline_percent = 0
            duration = 0

            if project.date_start and project.date:
                total_days = (project.date - project.date_start).days
                elapsed_days = (today - project.date_start).days

                if total_days > 0:
                    timeline_percent = round((elapsed_days / total_days) * 100, 2)
                    duration = total_days

            dashboard_data.append({
                'id': project.id,
                'name': project.name,
                'planned_start': project.date_start,
                'planned_end': project.date,
                'duration': duration,
                'manager':project.user_id.name if project.user_id else "No Manager",
                'timeline_percent': timeline_percent,
                'project_value': project_value,
                'invoiced': invoiced,
                'invoice_due': invoice_due,
                'billing_percent': round((invoiced / project_value) * 100, 2) if project_value else 0,
                'task_summary': {
                    'done': done,
                    'progress': progress,
                    'pending': total_tasks - done - progress,
                },
                'completion': completion,
            })
        return dashboard_data

    def _get_kpis(self, projects):

        today = date.today()

        total_projects = len(projects)
        ongoing = 0
        completed = 0
        delayed = 0

        for project in projects:

            if project.stage_id and project.stage_id.fold:
                completed += 1
            else:
                ongoing += 1

            if project.date and project.date < today:
                delayed += 1

        # Avoid division error
        def percent(value):
            return round((value / total_projects) * 100, 0) if total_projects else 0

        return [
            {
                "label": "Total Projects",
                "value": total_projects,
                "percent": 100,
            },
            {
                "label": "Ongoing",
                "value": ongoing,
                "percent": percent(ongoing),
            },
            {
                "label": "Completed",
                "value": completed,
                "percent": percent(completed),
            },
            {
                "label": "Delayed",
                "value": delayed,
                "percent": percent(delayed),
            },
        ]

    def _get_status_chart(self, projects):

        today = date.today()

        ongoing = 0
        completed = 0
        delayed = 0

        for project in projects:

            if project.stage_id and project.stage_id.fold:
                completed += 1
            else:
                ongoing += 1

            if project.date and project.date < today:
                delayed += 1

        return {
            "labels": ["Ongoing", "Completed", "Delayed"],
            "datasets": [{
                "data": [ongoing, completed, delayed],
                "backgroundColor": ["#198754", "#0dcaf0", "#dc3545"]
            }]
        }

    def _get_projects_per_manager_chart(self, projects):

        manager_map = {}

        for project in projects:

            manager_name = project.user_id.name if project.user_id else "No Manager"

            if manager_name not in manager_map:
                manager_map[manager_name] = 0

            manager_map[manager_name] += 1

        labels = list(manager_map.keys())
        data = list(manager_map.values())

        return {
            "labels": labels,
            "datasets": [{
                "label": "Projects",
                "data": data,
                "backgroundColor": "#0d6efd",
            }]
        }


    """Equipments Dashboard"""

    @api.model
    def get_dashboard_eq_chart(self):
        fleet = self.env['fleet.vehicle'].sudo().search([])
        vehicle_list = []
        for v in fleet:
            vehicle_list.append({
                'id': v.id,
                'model': v.name,  # or v.model_id.name
                'license_plate': v.license_plate,
                'driver': v.driver_id.name if v.driver_id else '',
                'image_url': f'/web/image/fleet.vehicle/{v.id}/image_128'
            })
        allocations = self.env['equipment.allocation'].sudo().search([])

        total = len(fleet)

        # --- Equipment state counts using state_id.name ---
        state_counts = {}
        for state in fleet.mapped('state_id'):
            state_counts[state.name] = len(fleet.filtered(lambda v: v.state_id == state))

        # --- Allocation ---
        active_alloc = allocations.filtered(
            lambda a: a.end_date and a.end_date.date() >= fields.Date.today()
        )
        allocated = len(active_alloc)
        utilization = round((allocated / total) * 100, 2) if total else 0

        # --- Values and odometer ---
        total_value = sum(fleet.mapped('net_car_value') or [0])
        residual_value = sum(fleet.mapped('residual_value') or [0])
        avg_odometer = round(sum(fleet.mapped('odometer') or [0]) / total, 2) if total else 0

        # --- Project wise equipment count ---
        project_data = []
        projects = active_alloc.mapped('project_id')
        for project in projects:
            count = len(active_alloc.filtered(lambda a: a.project_id.id == project.id))
            project_data.append({
                'project': project.name,
                'count': count,
            })

        # --- Allocation Table ---
        allocation_lines = []
        for line in allocations:
            allocation_lines.append({
                'project': line.project_id.name if line.project_id else '',
                'equipment': line.equipment_id.name if line.equipment_id else '',
                'start': line.start_date,
                'end': line.end_date,
                'id': line.id,
                'status': line.loading_status if line.loading_status else '',
            })

        return {
            "kpis": {
                "Total Equipments": total,
                "Allocated": allocated,
                "Utilization": utilization,
                "Total value": total_value,
                "Residual value": residual_value,
                "Avg odometer": avg_odometer,
                # Add dynamic state counts here
            },
            "status_distribution": {
                **state_counts,
            },
            "project_data": project_data,
            "allocations": allocation_lines,
            "vehicles":vehicle_list
        }


    """Customer Dashboard"""
    @api.model
    def customer_dashboard(self):

        partners = self.env['res.partner']\
                .with_context(active_test=False)\
                .search([])
        orders = self.env['sale.order'].sudo().search([('state', '=', 'sale')])

        total_customers = len(partners)
        active_customers = len(partners.filtered(lambda p: p.active))
        inactive_customers = total_customers - active_customers
        total_revenue = sum(orders.mapped('amount_total'))

        avg_order = total_revenue / len(orders) if orders else 0
        lifetime_value = total_revenue / total_customers if total_customers else 0

        # KPI Cards
        kpi_cards = [
            {"label": "Total Customers", "value": total_customers, "color": "linear-gradient(45deg,#4e73df,#224abe)"},
            {"label": "Active Customers", "value": active_customers, "color": "linear-gradient(45deg,#1cc88a,#13855c)"},
            {"label": "Inactive Customers", "value": inactive_customers,
             "color": "linear-gradient(45deg,#e74a3b,#be2617)"},
            {"label": "Total Revenue", "value": round(total_revenue, 2),
             "color": "linear-gradient(45deg,#f6c23e,#dda20a)"},
            {"label": "Avg Order Value", "value": round(avg_order, 2),
             "color": "linear-gradient(45deg,#36b9cc,#258391)"},
            {"label": "Lifetime Value", "value": round(lifetime_value, 2),
             "color": "linear-gradient(45deg,#858796,#60616f)"},
        ]

        # Growth Data
        growth = defaultdict(int)
        for p in partners:
            month = p.create_date.strftime("%b")
            growth[month] += 1

        growth_data = {
            "labels": list(growth.keys()),
            "datasets": [{
                "label": "New Customers",
                "data": list(growth.values()),
                "borderColor": "#4e73df",
                "fill": True
            }]
        }

        # Revenue Trend
        trend = defaultdict(float)
        for o in orders:
            month = o.date_order.strftime("%b")
            trend[month] += o.amount_total

        revenue_trend = {
            "labels": list(trend.keys()),
            "datasets": [{
                "label": "Revenue",
                "data": list(trend.values()),
                "borderColor": "#1cc88a",
                "fill": True
            }]
        }

        # Category Data
        category = defaultdict(int)
        for p in partners:
            cat = p.category_id.name if p.category_id else "Other"
            category[cat] += 1

        category_data = {
            "labels": list(category.keys()),
            "datasets": [{
                "data": list(category.values()),
                "backgroundColor": ["#4e73df", "#1cc88a", "#f6c23e", "#e74a3b", "#36b9cc"]
            }]
        }

        # Top Customers
        revenue_dict = defaultdict(float)
        for o in orders:
            revenue_dict[o.partner_id.name] += o.amount_total

        sorted_rev = sorted(revenue_dict.items(), key=lambda x: x[1], reverse=True)[:5]

        top_customer_data = {
            "labels": [x[0] for x in sorted_rev],
            "datasets": [{
                "label": "Revenue",
                "data": [x[1] for x in sorted_rev],
                "backgroundColor": "#4e73df"
            }]
        }

        recent_customers = [{
            "name": p.name,
            "email": p.email,
            "phone": p.phone
        } for p in partners.sorted(key=lambda r: r.create_date, reverse=True)[:5]]

        no_order_customers = [{
            "name": p.name,
            "email": p.email
        } for p in partners if not orders.filtered(lambda o: o.partner_id == p)][:5]

        # -------------------------------------------------
        # CUSTOMER TABLE DATA
        # -------------------------------------------------

        customers = []

        for p in partners:
            customers.append({
                "id": p.id,
                "name": p.name,
                "email": p.email,
                "phone": p.phone,
                "salesperson": p.user_id.name if p.user_id else "",
                "total_invoiced": round(p.sudo().total_invoiced or 0.0, 2),
                "total_due": round(p.sudo().total_due or 0.0, 2),
                "active": p.active,
            })

        return {
            "kpi_cards": kpi_cards,
            "growth_data": growth_data,
            "revenue_trend": revenue_trend,
            "category_data": category_data,
            "top_customer_data": top_customer_data,
            "recent_customers": recent_customers,
            "no_order_customers": no_order_customers,
            "customers": customers
        }


    """Employee Dashboard"""
    @api.model
    def get_employee_dashboard_data(self):

        today = fields.Date.today()
        first_day = today.replace(day=1)

        Employee = self.env['hr.employee'].sudo()
        Timesheet = self.env['account.analytic.line'].sudo()
        Department = self.env['hr.department'].sudo()

        # ==============================
        # EMPLOYEE DATA
        # ==============================

        employees = Employee.with_context(active_test=False).search([])

        total_employees = len(employees)
        active_employees = len(employees.filtered(lambda e: e.active))
        inactive_employees = total_employees - active_employees
        total_departments = Department.search_count([])

        # ==============================
        # TIMESHEET DATA (THIS MONTH)
        # ==============================

        timesheets = Timesheet.search([
            ('date', '>=', first_day),
            ('date', '<=', today),
        ])

        total_hours = sum(timesheets.mapped('unit_amount'))

        billable_timesheets = timesheets.filtered(lambda l: l.so_line)
        billable_hours = sum(billable_timesheets.mapped('unit_amount'))

        non_billable_hours = total_hours - billable_hours

        utilization = 0
        if total_hours:
            utilization = round((billable_hours / total_hours) * 100, 2)

        # ==============================
        # EMPLOYEE HOURS SUMMARY
        # ==============================

        employee_data = []
        employee_hours_map = {}

        for emp in employees:
            emp_timesheets = timesheets.filtered(lambda l: l.employee_id.id == emp.id)

            emp_total = sum(emp_timesheets.mapped('unit_amount'))
            emp_billable = sum(
                emp_timesheets.filtered(lambda l: l.so_line).mapped('unit_amount')
            )

            employee_hours_map[emp.name] = emp_total

            employee_data.append({
                "id": emp.id,
                "name": emp.name,
                "department": emp.department_id.name if emp.department_id else '',
                "job": emp.job_title or '',
                "total_hours": round(emp_total, 2),
                "billable_hours": round(emp_billable, 2),
                "active": emp.active,
            })

        # ==============================
        # TOP 5 EMPLOYEES
        # ==============================

        top_employees = sorted(
            employee_hours_map.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        # ==============================
        # DEPARTMENT SUMMARY
        # ==============================

        dept_labels = []
        dept_counts = []

        departments = Department.search([])

        for dept in departments:
            dept_labels.append(dept.name)
            dept_counts.append(
                len(employees.filtered(lambda e: e.department_id.id == dept.id))
            )

        # ==============================
        # MONTHLY HOURS (LAST 6 MONTHS)
        # ==============================

        monthly_labels = []
        monthly_hours = []

        for i in range(6):
            month_start = fields.Date.add(first_day, months=-i)
            month_end = fields.Date.end_of(month_start, 'month')

            month_ts = Timesheet.search([
                ('date', '>=', month_start),
                ('date', '<=', month_end),
            ])

            monthly_labels.insert(0, month_start.strftime("%b %Y"))
            monthly_hours.insert(0, sum(month_ts.mapped('unit_amount')))

        # ==============================
        # RETURN DATA
        # ==============================
        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "inactive_employees": inactive_employees,
            "total_departments": total_departments,
            "total_hours": round(total_hours, 2),
            "billable_hours": round(billable_hours, 2),
            "non_billable_hours": round(non_billable_hours, 2),
            "utilization": utilization,
            "employees": employee_data,
            "top_employee_labels": [x[0] for x in top_employees],
            "top_employee_hours": [x[1] for x in top_employees],
            "department_labels": dept_labels,
            "department_counts": dept_counts,
            "monthly_labels": monthly_labels,
            "monthly_hours": monthly_hours,
        }

    @api.model
    def get_crm_dashboard_data(self):

        leads = self.env['crm.lead'].sudo().search([])

        total_leads = len(leads)
        opportunities = len(leads.filtered(lambda l: l.type == 'opportunity'))
        won = len(leads.filtered(lambda l: l.stage_id.is_won))
        lost = len(leads.filtered(lambda l: l.active is False))

        # Stage Distribution
        stage_data = defaultdict(int)
        for lead in leads:
            stage_data[lead.stage_id.name] += 1

        # Monthly Revenue
        revenue_data = defaultdict(float)
        for lead in leads.filtered(lambda l: l.stage_id.is_won):
            month = lead.create_date.strftime("%b")
            revenue_data[month] += lead.expected_revenue

        # Top Salespersons
        salespersons = defaultdict(lambda: {
            "name": "",
            "total": 0,
            "won": 0,
            "revenue": 0,
        })

        for lead in leads:
            user = lead.user_id.name or "No Salesperson"
            salespersons[user]["name"] = user
            salespersons[user]["total"] += 1
            if lead.stage_id.is_won:
                salespersons[user]["won"] += 1
                salespersons[user]["revenue"] += lead.expected_revenue

        top_salespersons = list(salespersons.values())

        return {
            "kpis": {
                "total_leads": total_leads,
                "opportunities": opportunities,
                "won": won,
                "lost": lost,
            },
            "stage_data": dict(stage_data),
            "revenue_data": dict(revenue_data),
            "top_salespersons": top_salespersons,
        }
