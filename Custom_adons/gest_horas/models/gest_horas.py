from odoo import models, fields


class Professor (models.Model):
    _name = "professor"
    _description = "entidade professor"

    name = fields.Char(
        string= "Nome", 
        required=True,
        size = 150,
        help = "Digite o seu nome"
    )

    Email = fields.Char(
        string= "Email", 
        required=True,
        size = 150
    )

    sexo = fields.Selection(
        [
         ('1', 'Masculino'),
         ('2', 'Feminino'),
        ],
        string= "Sexo",
        required=True
    )
    

class Cadeira (models.Model):
    _name = "cadeira"
    _description = "descricao das disciplinas lecionadas"


    Nome = fields.Char(
        string= "Nome", 
        required=True,
        size = 150,
        help = "nome da disciplina lecionada"
    )

    professor = fields.Many2one (
        'professor',
        string= "professor",
        required=True,
        help=' informe qual/qausi professores lecionam tal cadeira'

    )


class Sala (models.Model):
    _name = "sala"
    _description = "informacao da sala"

    tipo_de_sala = fields.Selection(
        [
         ('1', 'Sala Normal'),
         ('2', 'Anfiteatro'),
        ],
        string= "tipo", 
        required=True,
                
    )

    numero = fields.Integer(
        string= "Numero ",
        required=True,
        help='informe o numero da sala'
    )




