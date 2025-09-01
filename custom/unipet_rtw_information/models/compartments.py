from odoo import api, models, fields

class RTWTrailerCompartment(models.Model):
    _name = 'rtw_information.compartment'
    _description = 'Trailer Compartment'

    name = fields.Integer(
        string="Compartment No.",
        required=True,
        compute="_compute_number",
        store=True
    )
    capacity = fields.Float(
        string="Capacity"
    )
    quantity = fields.Float(
        string="Current Quantity"
    )

    vehicle_id = fields.Many2one(
        comodel_name='rtw_information.trailer',
        string="Trailer",
        ondelete="cascade",
        required=True
    )

    display_name = fields.Char(compute="_compute_display_name")

    @api.depends("vehicle_id.compartments")
    def _compute_number(self):
        for trailer in self.mapped("vehicle_id"):
            for index, comp in enumerate(trailer.compartments, start=1):
                comp.name = index
    
    @api.depends("name", "capacity")
    def _compute_display_name(self):
        for comp in self:
            comp.display_name = f"Compartment {comp.name} ({comp.capacity}L)"

    def name_get(self):
        return [(comp.id, comp.display_name or f"Compartment {comp.name}") for comp in self]




