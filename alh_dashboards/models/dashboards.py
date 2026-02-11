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

