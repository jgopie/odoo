from odoo import models, fields

class FleetVehicleCompartment(models.Model):
    _name = 'fleet.vehicle.compartment'
    _description = 'Trailer Compartment'

    name = fields.Char(
        string="Compartment No.",
        required=True
    )
    capacity = fields.Float(
        string="Capacity"
    )
    quantity = fields.Float(
        string="Current Quantity"
    )

    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string="Trailer",
        ondelete="cascade",
        required=True
    )
