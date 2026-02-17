/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class EmployeeDashboard extends Component {

    static template = "alh_dashboards.employee_dashboard";

    setup() {
        this.orm = useService("orm");
        this.charts = {};
        this.state = useState({
            total_employees: 0,
            active_employees: 0,
            inactive_employees: 0,
            total_departments: 0,
            total_hours: 0,
            billable_hours: 0,
            non_billable_hours: 0,
            utilization: 0,
            employees: [],
            top_employee_labels: [],
            top_employee_hours: [],
            department_labels: [],
            department_counts: [],
            monthly_labels: [],
            monthly_hours: [],
        });

        onMounted(async () => {
            await this.loadData();
        });
    }

    async loadData() {

        const result = await this.orm.call(
            "project.dashboard",
            "get_employee_dashboard_data",
            []
        );
        Object.assign(this.state, result);

        setTimeout(() => {
            this.renderCharts();
        }, 200);
    }

    renderCharts() {

        // Destroy existing charts
        Object.values(this.charts).forEach(chart => chart.destroy());

        // EMPLOYEE STATUS
        this.charts.status = new Chart(
            document.getElementById("employeeStatusChart"),
            {
                type: 'doughnut',
                data: {
                    labels: ["Active", "Inactive"],
                    datasets: [{
                        data: [
                            this.state.active_employees,
                            this.state.inactive_employees
                        ],
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '60%'
                }
            }
        );

        // DEPARTMENT
        this.charts.department = new Chart(
            document.getElementById("departmentChart"),
            {
                type: 'bar',
                data: {
                    labels: this.state.department_labels,
                    datasets: [{
                        label: "Employees",
                        data: this.state.department_counts,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                }
            }
        );

        // MONTHLY HOURS
        this.charts.monthly = new Chart(
            document.getElementById("monthlyHoursChart"),
            {
                type: 'line',
                data: {
                    labels: this.state.monthly_labels,
                    datasets: [{
                        label: "Total Hours",
                        data: this.state.monthly_hours,
                        fill: true,
                        tension: 0.3,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                }
            }
        );

        // BILLABLE
        this.charts.billable = new Chart(
            document.getElementById("billableChart"),
            {
                type: 'pie',
                data: {
                    labels: ["Billable", "Non-Billable"],
                    datasets: [{
                        data: [
                            this.state.billable_hours,
                            this.state.non_billable_hours
                        ],
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                }
            }
        );

        // TOP EMPLOYEES
        this.charts.top = new Chart(
            document.getElementById("topEmployeesChart"),
            {
                type: 'bar',
                data: {
                    labels: this.state.top_employee_labels,
                    datasets: [{
                        label: "Hours",
                        data: this.state.top_employee_hours,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                }
            }
        );
    }

}

registry
    .category("actions")
    .add("alh_dashboards.employee_dashboard", EmployeeDashboard);
