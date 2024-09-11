from odoo import models, fields


class Professor (models.Model):
    _name = "professor"
    _description = "entidade professor"

    name = fields.Char(
        string= "Nome"
    )