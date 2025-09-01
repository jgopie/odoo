from odoo import models, fields, api
from datetime import datetime, timedelta
class FuelDispatch(models.Model):
    _name = "distribution.fuel_dispatch"
    _description = "Fuel Dispatch"

    dispatch_datetime = fields.Datetime(
        required = True, 
        default=datetime.now() + timedelta(days=1),
        string="Dispatch Date & Time"
    )
    delivery_note_ref = fields.Char(string="Delivery Note Ref")
    invoice_num_ref = fields.Char(string="Invoice No. Ref")
    dispatch_from_location = fields.Selection(
        selection=[
            ("paria", "Paria - Bond"),
            ("caroni", "Caroni - Bond"),
            ("crb_storage", "CRB Storage Tanks"),
            ("freeport", "Freeport and Truck Storage"),
            ("chag_mhl", "Chaguaramas Storage MHL"),
            ("chag_eog", "Chaguaramas Storage EOG")
        ],
        string="Dispatch From Location",
        required=True,
    )
    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer Account",
        required=True,
        domain=[("is_company", "=", True)]
    )
    transport_method = fields.Selection(
        required=True,
        selection=[
            ("rtw", "RTW"),
            ("direct_tank", "Direct Tank"),
            ("vessel", "Vessel")
        ]
    )
    rtw_trailer = fields.Many2one(
        comodel_name="rtw_information.trailer",
        string="RTW Trailer"
    )
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sales Order"
    )
    is_verified = fields.Boolean(required=True, default=False, string="Verification Status")
    order_quantity = fields.Float(required=True, string="Order Quantity")
    line_ids = fields.One2many(
        comodel_name="distribution.fuel_dispatch.fuel_line",
        inverse_name="dispatch_id",
        string="Dispatch Lines",
    )

    @api.onchange('rtw_trailer')
    def _onchange_rtw_trailer(self):
        for dispatch in self:
            dispatch.line_ids = [(5, 0, 0)]


class FuelDispatchLine(models.Model):
    _name="distribution.fuel_dispatch.fuel_line"
    _description="Fuel Dispatch Line"
    dispatch_id = fields.Many2one(
        comodel_name="distribution.fuel_dispatch",
        string="Dispatch",
        ondelete="cascade"
    )
    compartment_id = fields.Many2one(
        comodel_name="rtw_information.compartment",
        string="Compartment",
    )
    quantity = fields.Float(string="Quantity Dispatched (L)")