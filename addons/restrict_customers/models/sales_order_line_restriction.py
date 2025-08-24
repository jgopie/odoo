from odoo import models, fields, api
from odoo import exceptions
from odoo.exceptions import ValidationError

class SaleOrderLineRestriction(models.Model):
    _inherit = "sale.order.line"

    @api.constrains('product_id', 'order_id')
    def _check_customer_approval(self):
        for line in self:
            partner = line.order_id.partner_id
            product_name = line.product_id.product_tmpl.name
            if product_name == "Diesel" and not partner.approved_diesel:
                raise ValidationError(f"Customer {partner.name} not approved to purchase Diesel.")
            elif product_name == "Gasoline" and not partner.approved_gasoline:
                raise ValidationError(f"Customer {partner.name} not approved to purchase Gasoline.")
            
class ResPartner(models.Model):
    _inherit = "res.partner"
    approved_diesel = fields.Boolean(string="Approved to purchase Diesel")
    approved_gasoline = fields.Boolean(string="Approved to purchase Gasoline")

    @api.model
    def write(self, vals):
        if not self.env.user.has_group('restrict_customers.group_fuel_approval_finance'):
            if 'approved_diesel' in vals or 'approved_gasoline' in vals:
                raise exceptions.UserError("You are not allowed to modify fuel approvals.")
        return super().write(vals)