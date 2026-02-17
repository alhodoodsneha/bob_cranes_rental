/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class CustomerDashboard extends Component {

    static template = "alh_dashboards.customer_dashboard";

    setup() {
        this.orm = useService("orm");

        this.state = useState({
            kpi_cards: [],
            growth_data: {},
            revenue_trend: {},
            category_data: {},
            top_customer_data: {},
            recent_customers: [],
            no_order_customers: [],
            customers: [],
            searchQuery: "",
            currentPage: 1,
            pageSize: 10,
        });

        onMounted(async () => {
            await this.loadData();
        });
    }

    async loadData() {

        const result = await this.orm.call(
            "project.dashboard",
            "customer_dashboard",
            []
        );

        this.state.kpi_cards = result.kpi_cards;
        this.state.growth_data = result.growth_data;
        this.state.revenue_trend = result.revenue_trend;
        this.state.category_data = result.category_data;
        this.state.top_customer_data = result.top_customer_data;
        this.state.recent_customers = result.recent_customers;
        this.state.no_order_customers = result.no_order_customers;
        this.state.customers= result.customers;

        setTimeout(() => {
            this.renderCharts();
        }, 200);
    }

    renderCharts() {

        new Chart(document.getElementById("growthChart"), {
            type: "line",
            data: this.state.growth_data
        });

        new Chart(document.getElementById("revenueTrendChart"), {
            type: "line",
            data: this.state.revenue_trend
        });

        new Chart(document.getElementById("categoryChart"), {
            type: "pie",
            data: this.state.category_data
        });

        new Chart(document.getElementById("statusChart"), {
            type: "doughnut",
            data: {
                labels: ["Active", "Inactive"],
                datasets: [{
                    data: [
                        this.state.kpi_cards[1]?.value || 0,
                        this.state.kpi_cards[2]?.value || 0
                    ],
                    backgroundColor: ["#1cc88a","#e74a3b"]
                }]
            }
        });

        new Chart(document.getElementById("topCustomerChart"), {
            type: "bar",
            data: this.state.top_customer_data
        });
    }

    get filteredCustomers() {
        const query = this.state.searchQuery.toLowerCase();

        return this.state.customers.filter(c =>
            (c.name && c.name.toLowerCase().includes(query)) ||
            (c.email && c.email.toLowerCase().includes(query)) ||
            (c.phone && c.phone.toLowerCase().includes(query))
        );
    }

    get totalPages() {
        return Math.ceil(this.filteredCustomers.length / this.state.pageSize) || 1;
    }

    get paginatedCustomers() {
        const start = (this.state.currentPage - 1) * this.state.pageSize;
        const end = start + parseInt(this.state.pageSize);

        return this.filteredCustomers.slice(start, end);
    }

    nextPage() {
        if (this.state.currentPage < this.totalPages) {
            this.state.currentPage++;
        }
    }

    prevPage() {
        if (this.state.currentPage > 1) {
            this.state.currentPage--;
        }
    }

}

registry
    .category("actions")
    .add("alh_dashboards.customer_dashboard", CustomerDashboard);
