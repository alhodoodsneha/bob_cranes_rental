/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class CRMDashboard extends Component {

    static template = "alh_dashboards.crm_dashboard";

    setup() {
        this.orm = useService("orm");
        this.charts = {};
        this.state = useState({
            kpis: {},
            stage_data: {},
            revenue_data: {},
            top_salespersons: [],
        });

        onMounted(async () => {
            await this.loadData();
        });
    }

    async loadData() {

        const result = await this.orm.call(
            "project.dashboard",
            "get_crm_dashboard_data",
            []
        );

        Object.assign(this.state, result);

        setTimeout(() => {
            this.renderCharts();
        }, 200);
    }

    renderCharts() {

        // Stage Chart
        new Chart(document.getElementById("stageChart"), {
            type: "doughnut",
            data: {
                labels: Object.keys(this.state.stage_data),
                datasets: [{
                    data: Object.values(this.state.stage_data),
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            }
        });

        // Revenue Chart
        new Chart(document.getElementById("revenueChart"), {
            type: "bar",
            data: {
                labels: Object.keys(this.state.revenue_data),
                datasets: [{
                    label: "Revenue",
                    data: Object.values(this.state.revenue_data),
                }]
            },
            options: {
                    responsive: true,
                    maintainAspectRatio: false,
                }
        });
    }

}

registry
    .category("actions")
    .add("alh_dashboards.crm_dashboard", CRMDashboard);
