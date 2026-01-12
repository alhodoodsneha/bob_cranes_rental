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
#    (AGPL v3) along with this program.fleet.vehicle
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, models, fields,_


class TechnicalSpecification(models.Model):
    _name = 'technical.specification'
    _description = 'Technical Specification'
    _rec_name = 'name'

    name = fields.Char(
        string="Name"
    )


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    account_asset_id = fields.Many2one(
        'account.asset',
        string="Asset"
    )

    depreciation_account = fields.Many2one(
        'account.account',
        string="Depreciation Account"
    )

    expense_account = fields.Many2one(
        'account.account',
        string="Expense Account"
    )

    type_equipment_id = fields.Selection([('equipment','Equipment'),
                                          ('lifting','Lifting Accessories'),
                                          ('trailers','Trailers'),
                                          ('other','Other')],
                                          string="Type"
                                         )
    project_loc = fields.Many2one(
        'stock.location',
        string='Stock Location'
    )

    location_history_ids = fields.One2many(
        'fleet.vehicle.location.history',
        'vehicle_id',
        string="Location History"
    )

    specification_line_ids = fields.One2many(
        'technical.specification.items',
        'fleet_id',
        string="Specification Items"
    )

    gps_device_id = fields.Char(
        string="GPS Device ID"
    )

    gps_enabled = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="GPS Enabled"
    )

    engine_hours_used = fields.Float(
        string="Engine Hours Used"
    )

    fuel_consumption = fields.Float(
        string="Fuel Consumption"
    )

    utilization_percentage = fields.Float(
        string="Utilization Percentage"
    )

    @api.model
    def create(self, vals):
        """ Create function inherited for create  """
        res = super(FleetVehicle, self).create(vals)
        asset_id = self.env['account.asset'].sudo().create({
            'name':res.name,
            'account_depreciation_id':res.depreciation_account.id,
            'account_depreciation_expense_id':res.expense_account.id,
            'vehicle_id':res.id,
        })
        res.account_asset_id = asset_id.id
        return res

    @api.onchange('model_id')
    def _onchange_model_id_create_spec_lines(self):
        for vehicle in self:
            lines = []
            vehicle.specification_line_ids = [(5, 0, 0)]

            if vehicle.model_id:
                for spec in vehicle.model_id.technical_specification_ids:
                    lines.append((0, 0, {
                        'technical_specification_id': spec.id,
                        'model_id': vehicle.model_id.id,
                    }))

            vehicle.specification_line_ids = lines

class FleetVehicleLocationHistory(models.Model):
    _name = 'fleet.vehicle.location.history'
    _description = 'Fleet Vehicle Location History'
    _rec_name = 'vehicle_id'
    _order = 'updated_on desc'

    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string="Equipment",
        required=True,
        ondelete='cascade'
    )

    source_location_id = fields.Many2one(
        'stock.location',
        string="Source Location",

    )

    destination_location_id = fields.Many2one(
        'stock.location',
        string="Destination Location",
    )

    updated_by = fields.Many2one(
        'res.users',
        string="Updated By",
        default=lambda self: self.env.user,
        readonly=True
    )

    updated_on = fields.Datetime(
        string="Updated On",
        default=fields.Datetime.now,
        readonly=True
    )



class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'
    _description = 'Fleet Vehicle Model'

    technical_specification_ids = fields.Many2many(
        'technical.specification',
        string="Technical Specifications"
    )


class TechnicalSpecificationItems(models.Model):
    _name = 'technical.specification.items'
    _description = 'Technical Specification Items'
    _rec_name = 'technical_specification_id'


    technical_specification_id = fields.Many2one(
        'technical.specification',
        string="Technical Specification"
    )

    value = fields.Char(
        string="Value"
    )

    fleet_id = fields.Many2one(
        'fleet.vehicle',
        string="Fleet"
    )

    model_id = fields.Many2one(
        'fleet.vehicle.model',
        string="Model"
    )