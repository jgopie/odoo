from odoo import api, fields, models


class Tractor(models.Model):
    _name = "rtw_information.tractor"
    _description = "Tractor Unit"

    name = fields.Char(required=True, string="License Plate")
    make = fields.Char(string="Tractor Make")
    model = fields.Char(string="Tractor Model")
    contractor = fields.Selection(selection=[
        ("sktl", "SKTL"),
        ("ldst", "LDST"),
        ("crb", "CRB")
    ])

class Trailer(models.Model):
    _name = "rtw_information.trailer"
    _description = "Trailer Unit"

    name = fields.Char(required=True, string="License Plate")
    is_rigid = fields.Boolean(required=True, default=True)
    manufacturer = fields.Char(string="Trailer Manufacturer")
    compartments = fields.One2many(
        comodel_name="rtw_information.compartment",
        inverse_name="vehicle_id",
        string="Compartments"
    )
    capacity = fields.Float(
        string="Capacity",
        compute="_compute_capacity",
        store=True
    )
    contractor = fields.Selection(selection=[
        ("sktl", "SKTL"),
        ("ldst", "LDST"),
        ("crb", "CRB")
    ])

    @api.depends("compartments.capacity")
    def _compute_capacity(self):
        for trailer in self:
            trailer.capacity = sum(trailer.compartments.mapped('capacity'))
