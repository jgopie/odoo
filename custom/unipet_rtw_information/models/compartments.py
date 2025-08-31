from odoo import api, models, fields

class RTWTrailerCompartment(models.Model):
    _name = 'rtw_information.compartment'
    _description = 'Trailer Compartment'

    name = fields.Integer(
        string="Compartment No.",
        required=True,
        compute="_compute_number",
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

    @api.depends("vehicle_id.compartments")
    def _compute_number(self):
        for trailer in self.mapped('vehicle_id'):
            # Use the One2many recordset order (safe even with NewId)
            for index, comp in enumerate(trailer.compartments, start=1):
                comp.name = index

