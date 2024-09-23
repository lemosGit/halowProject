from odoo import models, fields


#CRIANDO O MODELO DEPARTAMENTO 
class Departamento (models.Model):
    _name = "departamento"
    _description = "modelo dos departamentos"

    Departamento = fields.Char(
        string= "Departamento", 
        required=True,
        size = 150,
        help = "informe o seu departamento"
    )

#CRIANDO O MODELO/TABELA PROFESSOR 
class Professor (models.Model):
    _name = "professor"
    _description = "entidade professor"

    nome = fields.Char(
        string= "Nome", 
        required=True,
        size = 150,
        help = "Digite o seu nome"
    )

    email = fields.Char(
        string= "Email", 
        required=True,
        size = 150
    )

    telefone = fields.Integer(
        string= "Telefone",
        required=True
    )

    sexo = fields.Selection(
        [
         ('1', 'Masculino'),
         ('2', 'Feminino'),
        ],
        string= "Sexo",
        required=True
    )
    
    departamento = fields.Many2one(
        'departamento',
        string= "Departamento",
        required=True
    )

    carga_horaria_semanal = fields.Integer(
        string = "carga horaria semanal",
        required=True
    )

    data_contratacao = fields.Date(
        string = "data de contratacao",
        required=True
    )

    observacao = fields.Text(
        string = "Observacao",
        required=True
    )

#CRIANDO O MODELO/TABELA DISPONIBILIDADE
class Dipsonibilidade (models.Model):
    _name = "disponibilidade"
    _description = "modelo que informa a disponibilidade dos professores"

    Dia_semana = fields.Selection(
        [
         ('1', 'Segunda-feira'),
         ('2', 'Terca-feira'),
         ('3', 'Quarta-feira'),
         ('4', 'Quinta-feira'),
         ('5', 'Sexta-feira'),
        ],
        string= "dia da semana",
        required=True
    )

    hora_inicio = fields.Integer(
        string = "hora de inicio",
        required=True
    )

    hora_fim = fields.Integer(
        string = "hora de finalizacao",
        required=True
    )

    Professor = fields.Many2one(
        'professor',
        string= "professor",
        required=True
    )

#CRIANDO O MODELO/TABELA DISCIPLINA 
class disciplina (models.Model):
    _name = "disciplina"
    _description = "descricao das disciplinas lecionadas"

    nome = fields.Char(
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

#CRIANDO O MODELO/TABELA SALA 
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

#CRIACAO DA TABELA/MODELO PERIODO

#class Periodo (models.Model):
#    _name = "periodo"
#    _description = "turnos"

#    periodo = fields.Char(
#        string = "Turno",
#        required=True
#    )

#CRIACAO DA TABELA/MODELO HORARIO

class Horario (models.Model):
    _name = "horario"
    _description = "descricao dos horarios dos professores"

    professor = fields.Many2one(
        'professor',
        string= "professor",
        required=True
    )

    disponibilidade = fields.Many2one(
        'disponibilidade',
        string = "diponibilidade",
        required = True
    )
    
    disciplina = fields.Many2one(
        'disciplina',
        string = "disciplina",
        required=True
    )

    sala = fields.Many2one(
        'sala',
        string = "sala",
        required=True
    )

    dia_semana = fields.Selection(
        [
         ('1', 'Segunda-feira'),
         ('2', 'Terca-feira'),
         ('3', 'Quarta-feira'),
         ('4', 'Quinta-feira'),
         ('5', 'Sexta-feira'),
        ],
        string= "dia da semana",
        required=True
    )

    hora_inicio = fields.Integer(
        string = "hora de inicio",
        required=True
    )

    hora_fim = fields.Integer(
        string = "hora de finalizacao",
        required=True
    )
    



