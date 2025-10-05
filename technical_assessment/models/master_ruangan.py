from odoo import models, fields, _ # type: ignore

class MasterRuangan(models.Model):
    _name = 'master.ruangan'
    _description = 'Master Data Ruangan'
    _rec_name = 'nama_ruangan'

    _sql_constrains = [('unique_nama_ruangan', 'UNIQUE(nama_ruangan)', 'Nama ruangan tidak boleh sama!')]


    nama_ruangan = fields.Char(string='Nama Ruangan', required=True)
    tipe_ruangan = fields.Selection(
        [
            ('meetroom_kecil', 'Meeting Room Kecil'),
            ('meetroom_besar', 'Meeting Room Besar'),
            ('aula', 'Aula')
        ],
        required=True,
        string='Tipe Ruangan'
    )
    lokasi_ruangan = fields.Selection(
        [
            ('1a', '1A'),
            ('1b', '1B'),
            ('1c', '1C'),
            ('2a', '2A'),
            ('2b', '2B'),
            ('2c', '2C')
        ],
        required=True,
        string='Lokasi Ruangan'
    )
    foto_ruangan = fields.Binary(string='Foto Ruangan', required=True, attachment=True)
    kapasitas_ruangan = fields.Integer(string='Kapasitas Ruangan')
    keterangan = fields.Text(string='Keterangan')