from odoo import fields, models, _, api # type: ignore

class MasterProducts (models.Model):
    _name = 'test.master.products'
    _description = 'Master Products Test'
    _rec_name = 'product_name'





    unit_type = fields.Selection(
        [
            ("101", "BMW SERIES 1"),
            ("102", "BMW SERIES 2"),
            ("103", "BMW SERIES 3"),
            ("104", "BMW SERIES 4"),
            ("105", "BMW SERIES 5"),
            ("106", "BMW SERIES 6"),
            ("107", "BMW SERIES 7"),
            ("108", "BMW SERIES M"),
            ("109", "BMW X1"),
            ("110", "BMW X3"),
            ("111", "BMW X4"),
            ("112", "BMW X5"),
        ]
    )
    product_name = fields.Char(string="Product Name")
    construction_year = fields.Selection(
        [
            ("2022", "2022"),
            ("2023", "2023"),
            ("2024", "2024"),
            ("2025", "2025")
        ]
    )
    chasis = fields.Char()
    no_engine = fields.Char()
