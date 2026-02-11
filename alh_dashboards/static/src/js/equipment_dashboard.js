/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class EquipmentDashboard extends Component {

    static template = "alh_dashboards.equipment_dashboard";

    setup() {
        this.orm = useService("orm");

        this.state = useState({
            kpis: {},
            status_distribution: {},
            project_data: [],
            allocations: [],
            vehicles: [],
        });

        onMounted(async () => {
            await this.loadData();
        });
    }

    async loadData() {

        const result = await this.orm.call(
            "project.dashboard",
            "get_dashboard_eq_chart",
            []
        );

        this.state.kpis = result.kpis || {};
        this.state.status_distribution = result.status_distribution || {};
        this.state.project_data = result.project_data || [];
        this.state.allocations = result.allocations || [];
        this.state.vehicles = result.vehicles || [];

        setTimeout(() => {
            this.renderCharts();
        }, 200);
    }

    renderCharts() {

        // STATUS CHART

        const ctxStatus = document.getElementById("statusChart");

        if (ctxStatus) {
            new Chart(ctxStatus, {
                type: "doughnut",
                data: {
                    labels: Object.keys(this.state.status_distribution),
                    datasets: [{
                        data: Object.values(this.state.status_distribution),
                        backgroundColor: [
                            "#198754",
                            "#ffc107",
                            "#dc3545",
                            "#0dcaf0"
                        ]
                    }]
                },
                options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '60%'
                    }
            });
        }

        // PROJECT CHART
        const ctxProject = document.getElementById("projectChart");

        if (ctxProject && this.state.project_data.length > 0) {
            new Chart(ctxProject, {
                type: "bar",
                data: {
                    labels: this.state.project_data.map(p => p.project),
                    datasets: [{
                        label: "Equipments",
                        data: this.state.project_data.map(p => p.count),
                        backgroundColor: "#0d6efd"
                    }]
                },
                options: { responsive: true }
            });
        }
    }

}

registry
    .category("actions")
    .add("alh_dashboards.equipment_dashboard", EquipmentDashboard);
