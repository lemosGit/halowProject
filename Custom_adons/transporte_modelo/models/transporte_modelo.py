from odoo import models, fields
 
class TranAluno (models.Model):
    _name = "trans.aluno"
    _description= "modulo do estudante"

#INFORMACOES PESSOAIS


    name = fields.Char(
        string= "Nome",
        size = 150,
        help = "campo para digitar o seu nome, Doutor",
        required=True
    )

    gender = fields.Selection(
        [
         ('1', 'Masculino'),
         ('2', 'Feminino'),
        ],
        string= "Sexo",
        required=True
    )

    date_birth = fields.Date(
        string = "Data de nascimento",
        required=True
        
    )

    parents_pai = fields.Many2one(
        'parents.model',
        string= "pai",
        required=True
    )
    parents_mae = fields.Many2one(
        'parents.model',
        string= "mae",
        required=True
    )

    nationality = fields.Selection(
        [
         ('1', 'Angolana'),
         ('2', 'Caboverdiana'),
         ('3', 'Guinense'),
         ('4', 'Brasileira'),
        ],
        string= "Nacionalidade",
        required=True
    )

    contact = fields.Integer(
        string= "Telemovel",
        required=True
    )

    email = fields.Char(
        string= "Email",
        size = 150,
        help = "campo para digitar o mail do estudante",
        required=True
    )

    phone = fields.Integer(
        string=" contacto de emergencia",
        required=True
    )  

#PAGE DOCUMENTOS

class AddressModel (models.Model):
    _name="address.model"
    _description=" modelo que referencia o endereco"

    street = fields.Char(
        string=" Rua",
        required=True
    )

    street2 = fields.Char(
        string= " Rua 2",
        required=True

    )

    province = fields.Selection(
        [
         ('1', 'Luanda'),
         ('2', 'Benguela'),
         ('3', 'Namibe'),
         
        ],
        string= "Provincia",
        required=True

    )

    country = fields.Selection(
        [
         ('1', 'Ao'),
         ('2', 'Moz'),
         ('3', 'Pt'),
         
        ],
        string= "Pais",
        required=True

    )
    phone = fields.Integer(
        string= "telemovel",
        required=True

    ) 
    email = fields.Char(
        string= "email",
        required=True
    )
    website = fields.Char(
        string= "website",
        required=True
    )


class Documents_model (models.Model):
    _name="documents.model"
    _description = " all documentos"

    doctype = fields.Selection(
         [
         ('1', 'NIF'),
         ('2', 'Bilhete de identidade'),
         ('3', 'Passaporte'),
         
        ],
        string= "Tipo de documento",
        required=True
    )

    numberdoc = fields.Char(
        string= "Numero",
        required=True
    )


    dataemi = fields.Date(
        string= "Emissao",
        required=True
        
    )

    dataval = fields.Date(
        string= "Validade",
        required=True
        
    )

class ParentsModel (models.Model):
    _name= "parents.model" 
    _description= "pais registrados"

    name_parent = fields.Char(
        string= "Nome",
        size = 150,
        help = "campo para digitar o seu nome, Doutor",
        required=True
    )

    gender_parent = fields.Selection(
        [
         ('1', 'Masculino'),
         ('2', 'Feminino'),
        ],
        string= "Sexo",
        required=True
    )

    contact_parent = fields.Integer(
        string= "Telemovel",
        required=True
    )


    nationality_parent = fields.Selection(
        [
         ('1', 'Angolana'),
         ('2', 'Caboverdiana'),
         ('3', 'Guinense'),
         ('4', 'Brasileira'),
        ],
        string= "Nacionalidade",
        required=True
    )


    email_parent = fields.Char(
        string= "Email",
        size = 150,
        help = "campo para digitar o mail do estudante",
        required=True
    )

    phone_parent = fields.Integer(
        string=" contacto de emergencia",
        required=True
    )

    address = fields.Char(
        string= "endereco",
        required=True
    )