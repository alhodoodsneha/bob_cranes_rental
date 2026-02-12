/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ActiveProjectsDashboard extends Component {
    static template = "alh_dashboards.active_projects_dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            kpis: [],
            projects: [],
            status_chart: {},
            managerChart: {},
        });

        onMounted(async () => {
            await this.loadData();
        });
    }

    async loadData() {

        const result = await this.orm.call(
            "project.dashboard",
            "get_dashboard_data",
            []
        );

        this.state.projects = result.projects;
        this.state.kpis = result.kpis;
        this.state.status_Chart = result.status_chart;
        this.state.managerChart = result.manager_chart;

        setTimeout(() => {
            this.renderCharts();
        }, 200);
    }

    renderCharts() {
        // Status Pie Chart
        new Chart(document.getElementById("statusChart"), {
            type: 'pie',
            data: this.state.status_Chart,
            options: {
                responsive: true,
                maintainAspectRatio: false   // 👈 important
            }
        });

        // Manager Bar Chart
        new Chart(document.getElementById("managerChart"), {
            type: 'bar',
            data: this.state.managerChart,
            options: {
                responsive: true,
                maintainAspectRatio: false   // 👈 important
            }
        });

        this.state.projects.forEach(project => {

            const done = project.task_summary.done || 0;
            const inProgress = project.task_summary.progress || 0;
            const pending = project.task_summary.pending || 0;

            console.log(inProgress)

            const total = done + inProgress + pending;
            const ctx = document.getElementById("taskChart_" + project.id);

            if (total === 0) {
                ctx.parentElement.innerHTML = `
                    <div class="d-flex justify-content-center align-items-center h-100 text-muted">
                        No Task Data Available
                    </div>
                `;
            }else{

                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Done', 'In Progress', 'Pending'],
                        datasets: [{
                            data: [
                                project.task_summary.done,
                                project.task_summary.progress,
                                project.task_summary.pending
                            ],
                            backgroundColor: ['#198754', '#ffc107', '#dc3545']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '60%'
                    }
                });
            }
        });
    }
}

registry
    .category("actions")
    .add("alh_dashboards.active_projects_dashboard", ActiveProjectsDashboard);
