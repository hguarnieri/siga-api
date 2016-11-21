from flask import Flask
from flask import request
from bs4 import BeautifulSoup
import json

# Login imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# PARAMETROS
TEST_MODE = 0

class Aula():
    titulo = ""
    turma = ""
    professores = []
    horarios = []

    def __init__(self):
        self.titulo = ""
        self.turma = ""
        self.professores = []
        self.horarios = []


def toJSON(html):
    if TEST_MODE:
        soup = BeautifulSoup(open("siga.html"), 'html.parser')
    else:
        soup = BeautifulSoup(html, 'html.parser')

    aulas = []
    lines = soup.select('#inscricao-resultados-form:atividades-inscritas-table tr')
    for line in lines[1:-1]:
        #print(line)
        aula = Aula()
        horarios = line.select('.horarios-turma li')
        for horario in horarios:
            aula.horarios.append(horario.string)

        professores = line.select('.ministrantes-turma li')
        for professor in professores:
            aula.professores.append(professor.string)

        titulo = line.select('.rf-dt-c')[0]
        turma = line.select('.rf-dt-c')[1]
        aula.titulo = titulo.string
        aula.turma = turma.string

        aulas.append(aula)

    return json.dumps([aula.__dict__ for aula in aulas])

# Functions
def loginSiga(username, password):
    driver = webdriver.PhantomJS()
    driver.set_window_size(1024, 768) # optional
    driver.get('https://sistemas.ufscar.br/siga/')

    formularioLogin = driver.find_element_by_id("login")
    campoUsuario = driver.find_element_by_name("login:usuario")
    campoSenha = driver.find_element_by_name("login:password")
    botaoLogin = driver.find_element_by_name("login:j_idt39")

    campoUsuario.send_keys(username)
    campoSenha.send_keys(password)

    botaoLogin.click()

    driver.get('https://sistemas.ufscar.br/siga/paginas/home.xhtml')
    driver.get('https://sistemas.ufscar.br/siga/paginas/aluno/listMatriculas.xhtml')

    try:
        botaoMatricula = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "aluno-matriculas-form:motivo-suspensao-table:0:j_idt90"))
        )

        # Abre opcoes de matricula
        botaoMatricula.click();

        botaoInscricoes = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "acoes-matriculas-form:solicitacao-inscricao-link"))
        )

        # Abre inscricoes
        botaoInscricoes.click();

        tabelaPeriodoRegular = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "inscricao-resultados-form:periodo-regular-andamento-table"))
        )

        # Abre o ultimo periodo
        botaoPeriodo = driver.find_element_by_xpath("//a[contains(@id,'inscricao-resultados-form:periodo-regular-andamento-table:0:j_idt')]")
        botaoPeriodo.click()

        tabelaPeriodoRegular = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "inscricao-resultados-form:atividades-inscritas-table"))
        )

        return toJSON(driver.page_source.encode('ascii', 'ignore'))
    finally:
        driver.quit()

app = Flask(__name__)

@app.route("/")
def hello():
    return loginSiga(request.args.get('user'), request.args.get('password'))

if __name__ == "__main__":
    app.run()
