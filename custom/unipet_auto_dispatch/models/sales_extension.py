from odoo import models, api, fields

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _eligible_for_dispatch(self):
        return self.product_id and self.product_id.categ_id.name == "Fuel"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line._eligible_for_dispatch():
                self.env["distribution.fuel_dispatch"].create({
                    "dispatch_datetime": line.order_id.commitment_date or fields.Datetime.now(),
                    "dispatch_from_location": "paria",
                    "customer_id": line.order_id.partner_id.id,
                    "order_quantity": line.product_uom_qty,
                    "transport_method": "direct_tank",
                    "sale_order_line_id": line.id,
                    "product_id": line.product_id.id,
                })
        return lines

    def write(self, vals):
        res = super().write(vals)
        for line in self:
            dispatch = self.env["distribution.fuel_dispatch"].search([
                ("sale_order_line_id", "=", line.id)
            ])
            if line._eligible_for_dispatch():
                if dispatch:
                    dispatch.write({
                        "order_quantity": line.product_uom_qty,
                        "customer_id": line.order_id.partner_id.id,
                        "dispatch_datetime": line.order_id.commitment_date or fields.Datetime.now(),
                        "product_id": line.product_id.id,
                    })
                else:
                    self.env["distribution.fuel_dispatch"].create({
                        "dispatch_datetime": line.order_id.commitment_date or fields.Datetime.now(),
                        "dispatch_from_location": "paria",
                        "customer_id": line.order_id.partner_id.id,
                        "order_quantity": line.product_uom_qty,
                        "transport_method": "direct_tank",
                        "sale_order_line_id": line.id,
                        "product_id": line.product_id.id,
                    })
            else:
                dispatch.unlink()
        return res
