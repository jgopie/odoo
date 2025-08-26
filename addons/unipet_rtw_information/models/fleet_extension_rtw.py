from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    compartment_ids = fields.One2many(
        comodel_name='fleet.vehicle.compartment',
        inverse_name='vehicle_id',
        string="Compartments"
    )

    quantity_total = fields.Float(
        string="Total Quantity",
        compute='_compute_total_quantity',
        store=True
    )

    @api.depends('compartment_ids.quantity')
    def _compute_total_quantity(self):
        for vehicle in self:
            if vehicle.category_id and vehicle.category_id.name == 'RTW Trailer':
                vehicle.quantity_total = sum(vehicle.compartment_ids.mapped('quantity'))
            else:
                vehicle.quantity_total = 0.0


class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'

    # Extend the selection values for Vehicle Type on the model form
    vehicle_type = fields.Selection(selection_add=[
        ('rtw_tractor', 'RTW Tractor'),
        ('rtw_trailer', 'RTW Trailer'),
    ], ondelete={
        'rtw_tractor': 'set default',
        'rtw_trailer': 'set default',
    })
