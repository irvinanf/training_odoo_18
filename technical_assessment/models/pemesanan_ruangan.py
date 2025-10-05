from odoo import models, fields, api # type: ignore
from odoo.exceptions import ValidationError # type: ignore

class PemesananRuangan(models.Model):
    _name='pemesanan.ruangan'
    _description='Pemesanan Ruangan Meeting'
    _rec_name = 'no_pemesanan'
    _order = 'no_pemesanan desc'

    _sql_constrains = [
        ('unique_nama_pemesan',
         'UNIQUE(nama_pemesan)',
         'Nama pemesan tidak boleh sama!')
         ]
    
    
    @api.constrains('ruangan', 'tgl_pemesanan')
    def _check_double_booking(self):
        for record in self:
            existing = self.search([
                ('ruangan', '=', record.ruangan.id),
                ('tgl_pemesanan', '=', record.tgl_pemesanan),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError("Ruangan sudah dipesan pada tanggal tersebut.")

    
    def create(self, vals):
        if vals.get('no_pemesanan', 'New') == 'New':
            vals['no_pemesanan'] = self.env['ir.sequence'].next_by_code('pemesanan.ruangan') or 'New'
            return super(PemesananRuangan, self).create(vals)
        
    def action_approve(self):
        for record in self:
            record.status_pemesanan="on_going"
    
    def action_done(self):
        self.ensure_one()
        if self.status_pemesanan == "on_going":
            self.status_pemesanan = "done"
    
    no_pemesanan = fields.Char(string='No. Pemesanan', 
                               required=True, 
                               copy=False, readonly=True, default='New')
    ruangan = fields.Many2one('master.ruangan', string="Ruangan", required=True)
    nama_pemesan = fields.Char(string='Nama Pemesan', required=True)
    tgl_pemesanan = fields.Date(string='Tanggal Pemesanan', required=True)
    status_pemesanan = fields.Selection(
        [
            ('draft', 'Draft'),
            ('on_going', 'On Going'),
            ('done', 'Done')
        ],
        string='Status Pemesanan',
        default='draft'
    )
    catatan_pemesanan = fields.Text(string='Catatan Pemesanan')