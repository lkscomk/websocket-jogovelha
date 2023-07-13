from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import uuid
import random
import json

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", cors_credentials=False)


@socketio.on('disconnect')
def disconnect():
  emit('jogadorSaiu', broadcast=True)


@socketio.on('jogarPartida')
def jogarPartida(conteudo):
  simbolo = conteudo["simbolo"]
  partida_id = conteudo["id"]
  jogo = conteudo["jogo"]
  if jogo < 1 or jogo > 9:
    mensagem = {"message": "Jogo inválido. Deve estar entre 1 e 9."}, 400
  # Carrega os dados existentes do arquivo JSON
  try:
    with open('banco.json', 'r') as f:
      usuarios = json.load(f)
  except:
    usuarios = []

  # Verifica se o e-mail já está cadastrado
  for usuario in usuarios:
    if usuario['id'] == partida_id:
      if usuario['jogos'][jogo - 1] == '':
        usuario['jogos'][jogo - 1] = simbolo
        if simbolo == 'x':
          usuario['atualVez'] = usuario['idO']
        else:
          usuario['atualVez'] = usuario['idX']
        # Salva os dados no arquivo JSON
        with open('banco.json', 'w') as f:
          json.dump(usuarios, f, ensure_ascii=False)

        jogo = usuario['jogos']
        if (jogo[0] == jogo[1] and jogo[1] == jogo[2] and jogo[2] != ''):
          vencedor = usuario['idO'] if jogo[0] == 'o' else usuario['idX']
        elif (jogo[3] == jogo[4] and jogo[4] == jogo[5] and jogo[5] != ''):
          vencedor = usuario['idO'] if jogo[3] == 'o' else usuario['idX']
        elif (jogo[6] == jogo[7] and jogo[7] == jogo[8] and jogo[8] != ''):
          vencedor = usuario['idO'] if jogo[6] == 'o' else usuario['idX']
        elif (jogo[0] == jogo[3] and jogo[3] == jogo[6] and jogo[6] != ''):
          vencedor = usuario['idO'] if jogo[0] == 'o' else usuario['idX']
        elif (jogo[1] == jogo[4] and jogo[4] == jogo[7] and jogo[7] != ''):
          vencedor = usuario['idO'] if jogo[1] == 'o' else usuario['idX']
        elif (jogo[2] == jogo[5] and jogo[5] == jogo[8] and jogo[8] != ''):
          vencedor = usuario['idO'] if jogo[2] == 'o' else usuario['idX']
        elif (jogo[6] == jogo[4] and jogo[4] == jogo[2] and jogo[2] != ''):
          vencedor = usuario['idO'] if jogo[6] == 'o' else usuario['idX']
        elif (jogo[0] == jogo[4] and jogo[4] == jogo[8] and jogo[8] != ''):
          vencedor = usuario['idO'] if jogo[0] == 'o' else usuario['idX']
        else:
          vencedor = 'empate'
          for x in range(len(jogo)):
            if jogo[x] == '':
              vencedor = False

        mensagem = {
          "id": partida_id,
          "jogo": usuario['jogos'],
          "atualVez": usuario['atualVez'],
          "vencedor": vencedor
        }
      else:
        mensagem = {
          "message": 'Está casa já foi preenchida por outro usuário'
        }, 400

  emit('jogarPartida', mensagem, broadcast=True)


@socketio.on('entradaSala')
def entradaSala(conteudo):
  emit('jogadorEntrou', conteudo, broadcast=True)


@socketio.on('zerarJogo')
def zerarJogo(conteudo):
  partidaId = conteudo["partidaId"]

  # Carrega os dados existentes do arquivo JSON
  try:
    with open('banco.json', 'r') as f:
      usuarios = json.load(f)
  except:
    usuarios = []

  # Verifica se o e-mail já está cadastrado
  for usuario in usuarios:
    if usuario['id'] == partidaId:
      usuario['jogos'] = [""] * 9
      mensagem = {
        "id": partidaId,
        "jogo": usuario['jogos'],
        "atualVez": conteudo["atualVez"]
      }

  # Salva os dados no arquivo JSON
  with open('banco.json', 'w') as f:
    json.dump(usuarios, f, ensure_ascii=False)

  emit('zerarJogo', mensagem, broadcast=True)

  return {"id": partidaId}, 200


@app.route('/criar-sala', methods=['POST'])
def criarSala():
  partida_id = str(uuid.uuid4())

  # Carrega os dados existentes do arquivo JSON
  try:
    with open('banco.json', 'r') as f:
      usuarios = json.load(f)
  except:
    usuarios = []

  # Adiciona os novos dados ao array de usuários
  usuarios.append({
    "id": partida_id,
    "jogadorX": '',
    "idX": '',
    "jogadorO": '',
    "idO": '',
    "jogos": [""] * 9,
    "atualVez": ""
  })

  # Salva os dados no arquivo JSON
  with open('banco.json', 'w') as f:
    json.dump(usuarios, f, ensure_ascii=False)

  return {"id": partida_id, "mensagem": "Jogo criado com sucesso"}, 200


@app.route('/remover-jogador', methods=['POST'])
def removerJogador():
  dados = request.get_json()

  partidaId = dados.get("partidaId")
  if not partidaId:
    return {"erro": "PartidaId é obrigatório."}

  jogadorId = dados.get("jogadorId")
  if not jogadorId:
    return {"erro": "jogadorId é obrigatório."}

  # Carrega os dados existentes do arquivo JSON
  try:
    with open('banco.json', 'r') as f:
      usuarios = json.load(f)
  except:
    usuarios = []

  # Verifica se o e-mail já está cadastrado
  for usuario in usuarios:
    if usuario['id'] == partidaId:
      if usuario['idX'] == jogadorId:
        usuario['idX'] = ''
        usuario['jogadorX'] = ''
      else:
        usuario['jogadorO'] = ''
        usuario['idO'] = ''

  # Salva os dados no arquivo JSON
  with open('banco.json', 'w') as f:
    json.dump(usuarios, f, ensure_ascii=False)

  return {'mensagem': jogadorId}


@app.route('/criar-jogador', methods=['POST'])
def criarJogador():
  dados = request.get_json()
  partidaId = dados.get("partidaId")
  if not partidaId:
    return {"erro": "PartidaId é obrigatório."}
  nome = dados.get("nome")
  if not nome:
    return {"erro": "Nome é obrigatório."}
  simbolo = dados.get("simbolo")
  if not simbolo:
    return {"erro": "Simbolo é obrigatório."}

  valor = random.randint(1000, 9999)

  # Carrega os dados existentes do arquivo JSON
  try:
    with open('banco.json', 'r') as f:
      usuarios = json.load(f)
  except:
    usuarios = []

  # Verifica se o e-mail já está cadastrado
  for usuario in usuarios:
    if usuario['id'] == partidaId:
      if simbolo == 'x':
        usuario['jogadorX'] = nome if simbolo == 'x' else usuario['jogadorX']
        usuario['idX'] = valor if simbolo == 'x' else usuario['idX']
        usuario['atualVez'] = usuario['idX']
        enviar = {'jogadorId': usuario['idX']}
      else:
        usuario['jogadorO'] = nome if simbolo == 'o' else usuario['jogadorO']
        usuario['idO'] = valor if simbolo == 'o' else usuario['idO']
        usuario['atualVez'] = usuario['idO']
        enviar = {'jogadorId': usuario['idO']}

  # Salva os dados no arquivo JSON
  with open('banco.json', 'w') as f:
    json.dump(usuarios, f, ensure_ascii=False)

  return enviar


@app.route('/entrar-sala', methods=['POST'])
def entrarSala():
  dados = request.get_json()
  partidaId = dados.get("partidaId")

  if not partidaId:
    return {"erro": "PartidaId é obrigatório."}
  nome = dados.get("nome")
  if not nome:
    return {"erro": "Nome é obrigatório."}

  # Carrega os dados existentes do arquivo JSON
  try:
    with open('banco.json', 'r') as f:
      usuarios = json.load(f)
  except:
    usuarios = []

  valor = random.randint(1000, 9999)

  # Verifica se o e-mail já está cadastrado
  enviar = {'erro': 'A sala não foi encontrada.'}
  for usuario in usuarios:
    if usuario['id'] == partidaId:
      if usuario['jogadorO'] == '':
        usuario['jogadorO'] = nome
        usuario['idO'] = valor
        enviar = {
          "id": partidaId,
          "jogadorId": usuario['idO'],
          "simbolo": 'o',
          "nome": nome,
          "atualVez": usuario['atualVez'],
          "idAdversario": usuario['idX'],
          "nomeAdversario": usuario['jogadorX']
        }
      elif usuario['jogadorX'] == '':
        usuario['jogadorX'] = nome
        usuario['idX'] = valor
        enviar = {
          "id": partidaId,
          "jogadorId": usuario['idX'],
          "simbolo": 'x',
          "nome": nome,
          "atualVez": usuario['atualVez'],
          "idAdversario": usuario['idO'],
          "nomeAdversario": usuario['jogadorO']
        }
      else:
        enviar = {'erro': 'A sala está preenchida com todos os jogadores'}

  # Salva os dados no arquivo JSON
  with open('banco.json', 'w') as f:
    json.dump(usuarios, f, ensure_ascii=False)

  return enviar



if __name__ == '__main__':
  socketio.run(app, host='0.0.0.0')
