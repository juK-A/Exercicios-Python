from flask import Flask, jsonify, request, g
import sqlite3

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('bauru_participa.db')
        g.c = g.db.cursor()
    return g.db, g.c

# Criação da tabela de enquetes
@app.before_request
def create_tables():
    db, c = get_db()
    c.execute('''CREATE TABLE IF NOT EXISTS enquetes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, descricao TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS opcoes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, enquete_id INTEGER, opcao TEXT, votos INTEGER DEFAULT 0, FOREIGN KEY(enquete_id) REFERENCES enquetes(id))''')
    db.commit()
# 1. Criar Enquete
@app.route('/api/enquetes', methods=['POST'])
def criar_enquete():
    dados = request.get_json()
    titulo = dados.get('titulo')
    descricao = dados.get('descricao')

    if not titulo or not descricao:
        return jsonify({'error': 'Os campos título e descrição são obrigatórios.'}), 400

    db, c = get_db()
    c.execute("INSERT INTO enquetes (titulo, descricao) VALUES (?, ?)", (titulo, descricao))
    db.commit()
    return jsonify({'message': 'Enquete criada com sucesso.'}), 201

# 2. Listar Enquetes
@app.route('/api/enquetes', methods=['GET'])
def listar_enquetes():
    db, c = get_db()
    c.execute("SELECT * FROM enquetes")
    enquetes = c.fetchall()
    lista_enquetes = []
    for enquete in enquetes:
        enquete_dict = {
            'id': enquete[0],
            'titulo': enquete[1],
            'descricao': enquete[2]
        }
        lista_enquetes.append(enquete_dict)
    return jsonify(lista_enquetes), 200

# 3. Obter detalhes de uma enquete
@app.route('/api/enquetes/<int:id>', methods=['GET'])
def obter_enquete(id):
    db, c = get_db()
    c.execute("SELECT * FROM enquetes WHERE id = ?", (id,))
    enquete = c.fetchone()
    if enquete:
        enquete_dict = {
            'id': enquete[0],
            'titulo': enquete[1],
            'descricao': enquete[2]
        }
        return jsonify(enquete_dict), 200
    else:
        return jsonify({'error': 'Enquete não encontrada.'}), 404

# 4. Votar em uma opção de enquete
@app.route('/api/enquetes/<int:id>/votar', methods=['POST'])
def votar_enquete(id):
    dados = request.get_json()
    opcao_id = dados.get('opcao_id')

    if not opcao_id:
        return jsonify({'error': 'O ID da opção é obrigatório.'}), 400

    db, c = get_db()
    c.execute("UPDATE opcoes SET votos = votos + 1 WHERE id = ?", (opcao_id,))
    db.commit()
    return jsonify({'message': 'Voto registrado com sucesso.'}), 200

# 5. Resultados de uma enquete
@app.route('/api/enquetes/<int:id>/resultados', methods=['GET'])
def resultados_enquete(id):
    db, c = get_db()
    c.execute("SELECT opcao, votos FROM opcoes WHERE enquete_id = ?", (id,))
    resultados = c.fetchall()
    if resultados:
        resultados_dict = []
        for resultado in resultados:
            resultado_dict = {
                'opcao': resultado[0],
                'votos': resultado[1]
            }
            resultados_dict.append(resultado_dict)
        return jsonify(resultados_dict), 200
    else:
        return jsonify({'error': 'Enquete não encontrada ou sem opções.'}), 404

# 6. Visualizar opções de uma enquete
@app.route('/api/enquetes/<int:id>/opcoes', methods=['GET'])
def listar_opcoes(id):
    db, c = get_db()
    c.execute("SELECT opcao FROM opcoes WHERE enquete_id = ?", (id,))
    opcoes = c.fetchall()
    if opcoes:
        lista_opcoes = [opcao[0] for opcao in opcoes]
        return jsonify(lista_opcoes), 200
    else:
        return jsonify({'error': 'Enquete não encontrada ou sem opções.'}), 404

# 7. Adicionar a opção em uma enquete
@app.route('/api/enquetes/<int:id>/opcoes', methods=['POST'])
def adicionar_opcao(id):
    dados = request.get_json()
    opcao = dados.get('opcao')

    if not opcao:
        return jsonify({'error': 'O campo opção é obrigatório.'}), 400

    db, c = get_db()
    c.execute("INSERT INTO opcoes (enquete_id, opcao) VALUES (?, ?)", (id, opcao))
    db.commit()
    return jsonify({'message': 'Opção adicionada com sucesso.'}), 201

# 8. Deletar enquete
@app.route('/api/enquetes/<int:id>', methods=['DELETE'])
def deletar_enquete(id):
    db, c = get_db()
    c.execute("DELETE FROM enquetes WHERE id = ?", (id,))
    db.commit()
    if c.rowcount > 0:
        return jsonify({'message': 'Enquete deletada com sucesso.'}), 200
    else:
        return jsonify({'error': 'Enquete não encontrada.'}), 404

# 9. Deletar uma opção de uma enquete
@app.route('/api/enquetes/<int:id_enquete>/opcoes/<int:id_opcao>', methods=['DELETE'])
def deletar_opcao(id_enquete, id_opcao):
    db, c = get_db()
    c.execute("DELETE FROM opcoes WHERE id = ? AND enquete_id = ?", (id_opcao, id_enquete))
    db.commit()
    if c.rowcount > 0:
        return jsonify({'message': 'Opção deletada com sucesso.'}), 200
    else:
        return jsonify({'error': 'Opção não encontrada.'}), 404

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

if __name__ == '__main__':
    app.run(debug=True)