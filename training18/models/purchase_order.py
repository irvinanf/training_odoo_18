from odoo import models, fields, api, _ # type: ignore
from datetime import date
from odoo.exceptions import UserError

class PurchaseOrder (models.Model):
    _name = 'test.purchase.order'
    _description = 'Purchase Order'


    # @api.onchange("company_line_id")
    # def _onchange_company(self):
    #     for company in self:
    #         return self.env.company

    def action_approve(self):
        for record in self:
            record.status="approved"

    def action_confirm(self):
        for record in self:
            if record.status=="approved":
                record.status = "done"

    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('test.purchase.order') or 'New'
            return super(PurchaseOrder, self).create(vals)

    # def action_done(self):
    #     for record in self:
    #         if record.status=="Purchase Confirmed":
    #             record.status = "Done"

    name = fields.Char(string='No. Purchase Order', required=True, copy=False, readonly=True, default='New')
    branch = fields.Selection(
        [
            ("ho", "Head Office"),
            ("sh", "Saharjo"),
            ("hw","Hayam Wuruk"),
            ("tm", "Tomang"),
            ("sc", "Bekasi"),
            ("bn", "Soekarno Hatta")
        ],
        required=True,
    )
    division = fields.Selection(
        [
            ("unit", "Unit"),
            ("sparepart", "Sparepart"),
            ("umum", "Umum"),
            ("finance", "Finance")
        ],
        required=True
    )
    supplier_line_id = fields.Many2one("res.partner", copy=False, required=True)
    supplier_reference = fields.Char(string="Supplier Reference")
    supplier_doc_date = fields.Date()
    payment_term = fields.Selection(
        [
            ("120", "120 Days"),
            ("14", "14 Days"),
            ("180", "180 Days"),
            ("30", "30 Days"),
            ("3", "3 Days"),
            ("42", "42 Days"),
            ("45", "45 Days"),
            ("90", "90 Days"),
            ("immediate", "Immediate Payment")
        ],
        required=True
    )
    currency = fields.Many2one("res.currency", required=True)
    company_line_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    PO_type = fields.Selection(
        [
            ("asset", "Asset"),
            ("bi_stock", "BI Stock"),
            ("test_drive", "Test Drive Sell")
        ]
    )
    gr_physical_date = fields.Date()
    order_date = fields.Date()
    deliver_to = fields.Selection(
        [
            ("sh", "SAHARJO"),
            ("hw", "HAYAM WURUK"),
            ("tm", "TOMANG"),
            ("sc", "BEKASI"),
            ("bn", "SOEKARNO HATTA")
        ],
        required=True
    )

    status = fields.Selection(
        [
            ("draft", "Draft PO"),
            ("waiting_for_approval", "Waiting for Approval"),
            ("sent", "RFQ"),
            ("approved", "Purchase Confirmed"),
            ("done", "Done"),
            ("cancel", "Cancelled")
        ],
        default="draft", string="Status"
    )

   
    # product_line_ids = fields.One2many('test.product.po', 'product_PO',string="Product")
    # def debug_product_lines(self):
    #     import ipdb; ipdb.set_trace()


    product_line_ids = fields.One2many('test.purchase.order.line', 'purchase_order_id', string="Product Lines")

    
     
 
    
class TestProductPO(models.Model):
    _name = 'test.purchase.order.line' #'test.product.po'
    _description = 'Product Purchase Order'
    _rec_name = 'purchase_order_id'


    @api.depends("disc_dealer", "disc_dealer_top", "disc_lain")
    def _compute_disc_total(self):
        for purchase in self:
            purchase.disc_total = (purchase.disc_dealer + purchase.disc_dealer_top + purchase.disc_lain)

    @api.depends("unit_price", "disc_total")
    def _compute_dpp(self):
        for purchase in self:
            purchase.dpp = purchase.unit_price - purchase.disc_total
    
    @api.depends("dpp")
    def _compute_ppn(self):
        for purchase in self:
            if purchase.taxes=='ppn_in_12_excl':
                purchase.ppn = purchase.dpp * 0.12
            elif purchase.taxes=='ppn_in_11_excl':
                purchase.ppn = purchase.dpp * 0.11
            elif purchase.taxes=='ppn_in_12_incl':
                purchase.ppn = (purchase.dpp/1.12) * 0.12
            elif purchase.taxes=='ppn_in_11_incl':
                purchase.ppn = (purchase.dpp/1.11) * 0.11
            else:
                purchase.ppn = 0

    @api.depends("dpp")
    def _compute_pph_22(self):
        for purchase in self:
            if purchase.pph22==True:
                purchase.pph_22 = purchase.dpp * 0.015
            else:
                purchase.pph_22 = 0

    @api.depends("dpp", "ppn", "pph22")
    def _compute_subtotal(self):
        for purchase in self:
            if purchase.taxes=='ppn_in_12_excl':
                purchase.subtotal = purchase.dpp + purchase.ppn + purchase.pph_22
            elif purchase.taxes=='ppn_in_11_excl':
                purchase.subtotal = purchase.dpp + purchase.ppn + purchase.pph_22
            elif purchase.taxes=='ppn_in_12_incl':
                purchase.subtotal = purchase.dpp + purchase.pph_22
            elif purchase.taxes=='ppn_in_11_incl':
                purchase.subtotal = purchase.dpp + purchase.pph_22
            else:
                purchase.subtotal = purchase.dpp
            

    # @api.onchange("company_line_id")
    # def _onchange_company(self):
    #     for company in self:
    #         return self.env.company
        

    
    product_PO = fields.Many2one('test.master.products',string="Product")   
    company_line_id = fields.Many2one("res.company")
    purchase_qty = fields.Integer(default=1)
    satuan_unit = fields.Char(string="Product Unit of Measure", default="Unit(s)")
    unit_price = fields.Float(required=True)
    disc_dealer = fields.Float()
    disc_dealer_top = fields.Float()
    disc_lain = fields.Float()
    disc_total = fields.Float(compute='_compute_disc_total', store=True, readonly=True)
    dpp = fields.Float(compute='_compute_dpp', store=True, readonly=True)
    taxes = fields.Selection(
        [
            ("ppn_in_12_incl", "PPN IN Inc 12%"),
            ("ppn_in_12_excl", "PPN IN Exc 12%"),
            ("ppn_in_11_incl", "PPN IN Inc 11%"),
            ("ppn_in_11_excl", "PPN IN Exc 11%"),
        ]
    )
    ppn = fields.Float(compute='_compute_ppn')
    pph22 = fields.Boolean()
    pph_22 = fields.Float(compute='_compute_pph_22')
    subtotal = fields.Float(compute='_compute_subtotal', store=True)

    purchase_order_id = fields.Many2one('test.purchase.order', string="Purchase Order")


    freight_cost = fields.Float()
    ppnbm = fields.Float()  

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