{
    "name": "Restrict product purchases to approved customers",
    "version": "1.0",
    "summary": "Prevents sales orders for being generated for customers who are not approved to purchase defined products",
    "category": "Unipet/Custom",
    "depends": ["sale_management"],
    "data": [
        "security/security.xml",
        "views/res_partner_views.xml",
        ],
    "assets": {
        "web.assets_backend": [
            "restrict_customers/static/src/scss/style.scss",
        ],
    },
    "installable": True,
    "application": False,
}