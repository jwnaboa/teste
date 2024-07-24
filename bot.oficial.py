import telebot
import sqlite3
from telebot import types
from io import BytesIO
import os


# Configuração do bot
API_TOKEN = '7471322014:AAFjMG-VtzHInmzrllOYAlCoVOSp4274TAI'
bot = telebot.TeleBot(API_TOKEN)


# Caminho da pasta de armazenamento local
LOCAL_STORAGE_PATH = os.path.expanduser('~/Desktop/frentista')

# Cria a pasta local se não existir
os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)

#region criaçao Banco de dados
def create_database():
    
    db_path = 'frentistas_bot.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS peleiras (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        phone TEXT,
                        value TEXT,
                        region TEXT,
                        city TEXT,
                        link TEXT,
                        score FLOAT,
                        image TEXT,
                        description TEXT,
                        username TEXT,
                        ja_foi TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS encapadas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        phone TEXT,
                        value TEXT,
                        region TEXT,
                        city TEXT,
                        link TEXT,
                        score FLOAT,
                        image TEXT,
                        description TEXT,
                        username TEXT,
                        ja_foi TEXT
                        
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tds (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        report TEXT,
                        username TEXT,
                        score FLOAT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sugestoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        username TEXT,
                        sugestao TEXT
                    )''')
    
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuario_permitido 
    (username TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

# Cria o banco de dados ao iniciar o script
create_database()
#endregion

#region Funções para Gerenciar Usuários Permitidos
def add_usuario_permitido(username):
    try:
        conn = sqlite3.connect('frentistas_bot.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT OR IGNORE INTO usuario_permitido (username) VALUES (?)''', (username,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao adicionar usuário permitido: {e}")
    finally:
        conn.close()

def remover_usuario_permitido(username):
    try:
        conn = sqlite3.connect('frentistas_bot.db')
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM usuario_permitido WHERE username = ?''', (username,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao remover usuário permitido: {e}")
    finally:
        conn.close()

def usuario_permitido(username):
    try:
        conn = sqlite3.connect('frentistas_bot.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT username FROM usuario_permitido WHERE username = ?''', (username,))
        result = cursor.fetchone()
        return result is not None
    except sqlite3.Error as e:
        print(f"Erro ao verificar usuário permitido: {e}")
        return False
    finally:
        conn.close()
#endregion
        
# define um administrador do bot
usuario_adm = 5493230042 #  ID de usuário do Telegram que deseja ser adm
def admin_only(func):
    def wrapper(message):
        if message.from_user.id == usuario_adm:
            return func(message)
        else:
            bot.reply_to(message, "Apenas administradores podem executar este comando.")
    return wrapper

#define uma regra de restriçao de utilizaçao do bot
def restricted(func):
    def wrapper(message):
        if usuario_permitido(message.from_user.username) or message.from_user.id == usuario_adm:
            return func(message)
        else:
            bot.reply_to(message, "Você não tem permissão para usar este bot.")
    return wrapper  

#region add, remover e listar usuarios permitidos no bot
@bot.message_handler(commands=['add_usuario'])
@admin_only

def handle_add_user(message):
    try:
        username = message.text.split()[1].lstrip('@')
        add_usuario_permitido(username)
        bot.reply_to(message, f"Usuário @{username} adicionado com sucesso.")
    except IndexError:
        bot.reply_to(message, "Uso: /add_usuario <usuario>")

@bot.message_handler(commands=['remover_usuario'])
@admin_only

def handle_remove_user(message):
    try:
        username = message.text.split()[1].lstrip('@')
        remover_usuario_permitido(username)
        bot.reply_to(message, f"Usuário @{username} removido com sucesso.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Uso: /remover_usuario <usuario>")
    
def list_usuarios_permitidos():
    try:
        conn = sqlite3.connect('frentistas_bot.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT username FROM usuario_permitido''')
        usuarios = cursor.fetchall()
        conn.close()
        return usuarios
    except sqlite3.Error as e:
        print(f"Erro ao listar usuários permitidos: {e}")
        return []
    
@bot.message_handler(commands=['listar_usuarios'])
@admin_only
def handle_listar_usuarios(message):
    usuarios = list_usuarios_permitidos()
    if usuarios:
        resposta = "Usuários permitidos dentro do bot:\n\n" + "\n".join([f"@{usuario[0]}" for usuario in usuarios])
    else:
        resposta = "Nenhum usuário permitido encontrado."
    bot.send_message(message.chat.id, resposta)


#endregion


#region openai Gpt


#endregion

def verificar_existencia(campo, valor, tabela):
    """
    Verifica a existência de um valor em um campo específico de uma tabela.

    Parâmetros:
    - campo: Nome do campo a ser verificado (ex: "name" ou "phone").
    - valor: Valor a ser verificado.
    - tabela: Nome da tabela onde o valor será verificado (ex: "peleiras" ou "encapadas").

    Retorna:
    - True se o valor existir na tabela, False caso contrário.
    """
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    query = f"SELECT id FROM {tabela} WHERE {campo} = ?"
    cursor.execute(query, (valor,))
    registro = cursor.fetchone()
    conn.close()
    return registro is not None

# Exemplo de uso:
# verificar_existencia('name', 'Nome da Peleira', 'peleiras')
# verificar_existencia('phone', '123456789', 'encapadas')


#region metodo inserir e deletar categoria e td do bot
def insert_peleira(name, phone, value, region, city, link, score, image, description, username, ja_foi):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO peleiras (name, phone, value, region, city, link, score, image, description, username, ja_foi)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (name, phone, value, region, city, link, score, image, description, username, ja_foi))
    conn.commit()
    conn.close()

def insert_encapada(name, phone, value, region, city, link, score, image, description, username, ja_foi):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO encapadas (name, phone, value, region, city, link, score, image, description, username, ja_foi)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (name, phone, value, region, city, link, score, image, description, username, ja_foi))
    conn.commit()
    conn.close()

def delete_peleira(name):
    try:
        conn = sqlite3.connect('frentistas_bot.db')
        cursor = conn.cursor()
        
        # Obter o caminho da imagem da peleira
        cursor.execute('''SELECT image_path FROM peleiras WHERE name = ?''', (name,))
        image_path = cursor.fetchone()
        
        # Excluir todos os TDs relacionados a esta peleira
        cursor.execute('''DELETE FROM tds WHERE name = ?''', (name,))
        
        # Excluir a peleira
        cursor.execute('''DELETE FROM peleiras WHERE name = ?''', (name,))
        conn.commit()
        
        # Deletar a imagem localmente
        if image_path:
            try:
                os.remove(image_path[0])
            except Exception as e:
                print(f"Erro ao excluir a imagem localmente: {e}")
    except sqlite3.Error as e:
        print(f"Erro ao excluir peleira: {e}")
    finally:
        conn.close()

def delete_encapada(name):
    try:
        conn = sqlite3.connect('frentistas_bot.db')
        cursor = conn.cursor()
        
        # Obter o caminho da imagem da encapada
        cursor.execute('''SELECT image_path FROM encapadas WHERE name = ?''', (name,))
        
        image_path = cursor.fetchone()
        # Excluir todos os TDs relacionados a esta encapada
        cursor.execute('''DELETE FROM tds WHERE name = ?''', (name,))
        
        # Excluir a encapada
        cursor.execute('''DELETE FROM encapadas WHERE name = ?''', (name,))
        conn.commit()
        
        # Deletar a imagem localmente
        if image_path:
            try:
                os.remove(image_path[0])
            except Exception as e:
                print(f"Erro ao excluir a imagem localmente: {e}")
                
    except sqlite3.Error as e:
        print(f"Erro ao excluir encapada: {e}")
    finally:
        conn.close()

def insert_td(name, report, username, score):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO tds (name, report, username, score) VALUES (?, ?, ?, ?)''', (name, report, username, score))
    conn.commit()
    conn.close()
#endregion

#region atualizar cadastro peleira e encapada
# comando para atualizar cadastro
def update_record(table, id, field, value):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {table} SET {field} = ? WHERE id = ?", (value, id))
    conn.commit()
    conn.close()

update_context = {}

def get_ids_by_name(table, name):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {table} WHERE name LIKE ?", (f"%{name}%",))
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids

@bot.message_handler(commands=['atualizar_cadastro'])
def handle_atualizar(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Peleiras", callback_data="update_peleiras"))
    markup.add(types.InlineKeyboardButton("Encapadas", callback_data="update_encapadas"))
    bot.send_message(message.chat.id, "Escolha o cadastro que deseja atualizar:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["update_peleiras", "update_encapadas"])
def choose_update(call):
    update_context[call.message.chat.id] = {"table": call.data.split('_')[1]}
    msg = bot.send_message(call.message.chat.id, "Digite o nome da garota que deseja atualizar:")
    bot.register_next_step_handler(msg, get_name)
    # Remove os botões inline após o clique
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

def get_name(message):
    table = update_context[message.chat.id]["table"]
    name = message.text
    ids = get_ids_by_name(table, name)
    if ids:
        update_context[message.chat.id]["name"] = name
        markup = types.InlineKeyboardMarkup()
        fields = {
            "nome": "name",
            "telefone": "phone",
            "valor": "value",
            "regiao": "region",
            "cidade": "city",
            "link": "link",
            "imagem": "image",
            "descricao": "description"
        }
        for label, field in fields.items():
            markup.add(types.InlineKeyboardButton(label.capitalize(), callback_data=f"field_{field}"))
        bot.send_message(message.chat.id, "Escolha a informação que deseja atualizar:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"Nenhum registro encontrado para '{name}'.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("field_"))
def choose_field(call):
    field = call.data.split('_')[1]
    update_context[call.message.chat.id]["field"] = field
    # Remove os botões inline após o clique
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    if field == "region":
        markup = types.InlineKeyboardMarkup()
        regions = ["Leste", "Oeste", "Centro", "Sul", "Norte"]
        for region in regions:
            markup.add(types.InlineKeyboardButton(region, callback_data=f"region_{region}"))
        bot.send_message(call.message.chat.id, "Escolha a região:", reply_markup=markup)
    else:
        msg = bot.send_message(call.message.chat.id, f"Digite o novo valor para {field}:")
        bot.register_next_step_handler(msg, get_new_value)

@bot.callback_query_handler(func=lambda call: call.data.startswith("region_"))
def choose_region(call):
    chat_id = call.message.chat.id
    region = call.data.split('_')[1]
    update_context[chat_id]["value"] = region
    # Remove os botões inline após o clique
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    finalize_update(chat_id)

def get_new_value(message):
    chat_id = message.chat.id
    new_value = message.text
    update_context[chat_id]["value"] = new_value
    finalize_update(chat_id)

def finalize_update(chat_id):
    table = update_context[chat_id]["table"]
    name = update_context[chat_id]["name"]
    field = update_context[chat_id]["field"]
    new_value = update_context[chat_id]["value"]
    ids = get_ids_by_name(table, name)
    for id in ids:
        update_record(table, id, field, new_value)
    bot.send_message(chat_id, f"{field.capitalize()} atualizado para '{new_value}' no cadastro de {name}.")
    del update_context[chat_id]

#endregion

#region metodo listar 
def list_peleiras():
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM peleiras''')
    peleiras = cursor.fetchall()
    conn.close()
    return peleiras

def list_encapadas():
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM encapadas''')
    encapadas = cursor.fetchall()
    conn.close()
    return encapadas

def list_tds():
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM tds''')
    tds = cursor.fetchall()
    conn.close()
    return tds
#endregion

import re
def escape_markdown(text):
    escape_chars = r'\*_`['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)

#region manipular imagem, uploud e download
# Função para upload de imagem local
def salvar_imagem(image_data, image_name):
    try:
        image_path = os.path.join(LOCAL_STORAGE_PATH, image_name)
        with open(image_path, 'wb') as file:
            file.write(image_data.read())
        return image_path
    except Exception as e:
        print(f"Erro ao salvar a imagem localmente: {str(e)}")
        return None

# Função para carregar imagem local
def carregar_imagem(image_path):
    try:
        with open(image_path, 'rb') as file:
            return BytesIO(file.read())
    except Exception as e:
        print(f"Erro ao carregar a imagem localmente: {str(e)}")
        return None

def lidar_com_foto(message):
    try:
        photo = message.photo[-1]
        image_id = photo.file_id
        image_info = bot.get_file(image_id)
        image_data = bot.download_file(image_info.file_path)
        image_name = f"{message.from_user.id}_{image_id}.jpg"
        
        image_path = salvar_imagem(BytesIO(image_data), image_name)
        
        if image_path:
            bot.reply_to(message, "Imagem recebida e salva com sucesso!")
        else:
            bot.reply_to(message, "Erro ao salvar a imagem.")
    except Exception as e:
        bot.reply_to(message, f"Erro ao processar a imagem: {str(e)}")
#endregion   

#region inserir e manipular sugestoes
def inserir_sugestao(username, sugestao):
    try:
        conn = sqlite3.connect('frentistas_bot.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO sugestoes (username, sugestao) VALUES (?, ?)''', (username, sugestao))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao inserir sugestão: {e}")
    finally:
        conn.close()
        
@bot.message_handler(commands=['melhoria'])
@restricted
def handle_sugestao(message):
    msg = bot.send_message(message.chat.id, "Por favor, envie sua sugestão de melhoria:")
    bot.register_next_step_handler(msg, salvar_sugestao)

def salvar_sugestao(message):
    if message.text:
        username = message.from_user.username
        sugestao = message.text
        inserir_sugestao(username, sugestao)
        bot.send_message(message.chat.id, "Obrigado pela sua sugestão!")
    else:
        bot.send_message(message.chat.id, "Sugestão inválida. Por favor, tente novamente.")
        
def list_sugestoes():
    try:
        conn = sqlite3.connect('frentistas_bot.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT id, username, sugestao FROM sugestoes''')  # Include 'id' in the select statement
        sugestoes = cursor.fetchall()
        conn.close()
        return sugestoes
    except sqlite3.Error as e:
        print(f"Erro ao listar sugestões: {e}")
        return []
@bot.message_handler(commands=['listar_melhorias'])
@admin_only
def handle_listar_sugestoes(message):
    sugestoes = list_sugestoes()
    if sugestoes:
        resposta = "Sugestões de melhoria:\n\n" + "\n\n".join([f"ID {sugestao[0]} - @{sugestao[1]}: {sugestao[2]}" for sugestao in sugestoes])
    else:
        resposta = "Nenhuma sugestão encontrada."
    bot.send_message(message.chat.id, resposta)

def deletar_sugestao(sugestao_id):
    try:
        conn = sqlite3.connect('frentistas_bot.db')
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM sugestoes WHERE id = ?''', (sugestao_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao excluir sugestão: {e}")
    finally:
        conn.close()     

@bot.message_handler(commands=['concluir_sugestao'])
@admin_only
def handle_concluir_sugestao(message):
    try:
        sugestao_id = int(message.text.split()[1])
        deletar_sugestao(sugestao_id)
        bot.reply_to(message, f"Sugestão {sugestao_id} concluída e removida com sucesso.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Uso: /concluir_sugestao <id>")
    except Exception as e:
        bot.reply_to(message, f"Ocorreu um erro ao concluir a sugestão: {e}")

#endregion
        
# lista de comandos que se pode usar no bot  
comandos = {'\n'
    '**ADM **\n'
    '/start': 'Iniciar a interação com o bot.\n',
    '/add_usuario': 'Adicionar um usuário para poder usar o bot.\n',
    '/remover_usuario': 'Remover um usuário do bot.\n',
    '/listar_usuarios': 'Listar todos os usuários que podem usar o bot.\n',
    
    '** USUARIO **\n'
    '/melhoria': 'Usuario pode sugerir uma melhoria.\n',
    '/listar_melhorias': 'Listar todas as sugestões de melhoria.\n',
    '/concluir_sugestao': 'Marcar uma sugestão como concluída e removê-la.\n',
    '/ajuda': 'Listar todos os comandos disponíveis.\n',
}
@bot.message_handler(commands=['ajuda'])
def handle_comandos(message):
    resposta = "Comandos disponíveis:\n"
    for comando, descricao in comandos.items():
        resposta += f"{comando} - {descricao}\n"
    bot.send_message(message.chat.id, resposta)
##    

#region ja fui (pra quem quiser marcar que ja foi na menina()
@bot.message_handler(commands=['ja_fui'])
@restricted
def handle_ja_fui(message):
    bot.send_message(message.chat.id, "Digite o nome da peleira ou encapada que você visitou:")
    bot.register_next_step_handler(message, process_ja_fui)

def process_ja_fui(message):
    nome = message.text
    username = message.from_user.username
    if verificar_existencia_registro('peleiras', nome) or verificar_existencia_registro('encapadas', nome):
        msg = bot.send_message(message.chat.id, f"Você marcou que já visitou {nome}. Qual a nota que você daria (1-10)?")
        bot.register_next_step_handler(msg, process_nota, nome)
    else:
        bot.send_message(message.chat.id, f"Nome {nome} não encontrado no banco de dados. Por favor, verifique o nome e tente novamente.")

def process_nota(message, nome):
    try:
        nota = float(message.text)
        if nota < 1 or nota > 10:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "Nota inválida. Por favor, insira um número de 1 a 10.")
        return

    username = message.from_user.username
    if update_ja_foi(nome, username, nota):
        bot.send_message(message.chat.id, f"Obrigado por sua avaliação! Você deu nota {nota} para {nome}.")
    else:
        bot.send_message(message.chat.id, f"Você já marcou que visitou {nome}.")
    
    inserir_nota(nome, username, nota)

def inserir_nota(name, username, nota):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    
    # Atualizar a nota na tabela peleiras
    cursor.execute('''UPDATE peleiras SET score = ? WHERE name = ? AND (score IS NULL OR score < ?)''', (nota, name, nota))
    # Atualizar a nota na tabela encapadas
    cursor.execute('''UPDATE encapadas SET score = ? WHERE name = ? AND (score IS NULL OR score < ?)''', (nota, name, nota))
    
    conn.commit()
    conn.close()

def update_ja_foi(name, username, score):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    
    # Verificar e atualizar o campo ja_foi na tabela peleiras
    cursor.execute('''SELECT ja_foi FROM peleiras WHERE name = ?''', (name,))
    ja_foi = cursor.fetchone()
    if ja_foi:
        ja_foi = ja_foi[0] if ja_foi[0] else ""
        entry = f"@{username} - Nota: {score}"
        if entry in ja_foi.split('\n'):
            conn.close()
            return False
        else:
            ja_foi = ja_foi + '\n' + entry if ja_foi else entry
            cursor.execute('''UPDATE peleiras SET ja_foi = ? WHERE name = ?''', (ja_foi, name))
            conn.commit()

    # Verificar e atualizar o campo ja_foi na tabela encapadas
    cursor.execute('''SELECT ja_foi FROM encapadas WHERE name = ?''', (name,))
    ja_foi = cursor.fetchone()
    if ja_foi:
        ja_foi = ja_foi[0] if ja_foi[0] else ""
        entry = f"@{username} - Nota: {score}"
        if entry in ja_foi.split('\n'):
            conn.close()
            return False
        else:
            ja_foi = ja_foi + '\n' + entry if ja_foi else entry
            cursor.execute('''UPDATE encapadas SET ja_foi = ? WHERE name = ?''', (ja_foi, name))
            conn.commit()

    conn.close()
    return True

def verificar_existencia_registro(table, name):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {table} WHERE name = ?", (name,))
    registro = cursor.fetchone()
    conn.close()
    return registro is not None

def list_ja_fui():
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, username, nota
        FROM (
            SELECT name, username, nota FROM peleiras WHERE ja_foi IS NOT NULL
            UNION ALL
            SELECT name, username, nota FROM encapadas WHERE ja_foi IS NOT NULL
        )
    ''')
    ja_fui = cursor.fetchall()
    conn.close()
    return ja_fui

@bot.message_handler(commands=['listar_ja_fui'])
@admin_only
def handle_listar_ja_fui(message):
    ja_fui = list_ja_fui()
    if ja_fui:
        resposta = "Registros de visitas:\n" + "\n".join([f"{item[1]} visitou {item[0]} e deu nota {item[2]}" for item in ja_fui])
    else:
        resposta = "Nenhum registro de visita encontrado."
    bot.send_message(message.chat.id, resposta)


#endregion

user_data = {}

@bot.message_handler(commands=['start'])
@restricted

def mensagem_inicio(message):
    welcome_message = "Olá, frentista! Como posso ajudar você hoje?"

    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Cadastrar Peleira')
    btn2 = types.KeyboardButton('Cadastrar Encapada')
    btn3 = types.KeyboardButton('Cadastrar TD')
    btn4 = types.KeyboardButton('Buscar')
    btn5 = types.KeyboardButton('Listar')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

#region cadastro de peleira
@bot.message_handler(func=lambda message: message.text == 'Cadastrar Peleira')
@restricted
def handle_register_peleira(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn_back)
    bot.send_message(message.chat.id, "Digite o nome da peleira:", reply_markup=markup)
    bot.register_next_step_handler(message, ask_peleira_phone)

def ask_peleira_phone(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['name'] = message.text
    bot.send_message(message.chat.id, "Digite o telefone da peleira:")
    bot.register_next_step_handler(message, ask_peleira_value)

def ask_peleira_value(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['phone'] = message.text
    bot.send_message(message.chat.id, "Digite o valor da peleira:")
    bot.register_next_step_handler(message, ask_peleira_region)

def ask_peleira_region(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['value'] = message.text
    
    markup = types.InlineKeyboardMarkup()
    regions = ["Leste", "Oeste", "Centro", "Sul", "Norte"]

    for region in regions:
        markup.add(types.InlineKeyboardButton(region, callback_data=f"peleira_region_{region}"))
    
    bot.send_message(message.chat.id, "Selecione a região:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('peleira_region_'))
def handle_peleira_region_selection(call):
    region = call.data.split('_')[-1]
    user_data['region'] = region
    
    # Editar a mensagem para remover os botões
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    
    bot.send_message(call.message.chat.id, f"Região selecionada: {region}")
    bot.send_message(call.message.chat.id, "Digite a cidade da peleira:")
    bot.register_next_step_handler(call.message, ask_peleira_city)

def ask_peleira_city(message):
    user_data['city'] = message.text
    bot.send_message(message.chat.id, "Digite o link da peleira:")
    bot.register_next_step_handler(message, ask_peleira_description)

def ask_peleira_description(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['link'] = message.text
    bot.send_message(message.chat.id, "Digite uma breve descrição da peleira:")
    bot.register_next_step_handler(message, ask_peleira_image)

def ask_peleira_image(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return

    user_data['description'] = message.text
    bot.send_message(message.chat.id, "Envie uma imagem para a peleira:")
    bot.register_next_step_handler(message, save_peleira_image)

def save_peleira_image(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return

    if message.photo:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image_name = f"peleira_{user_data['name'].replace(' ', '_')}.jpg"
        image_data = BytesIO(downloaded_file)
        
        image_path = salvar_imagem(image_data, image_name)
        
        if image_path:
            insert_peleira(
                user_data['name'],
                user_data['phone'],
                user_data['value'],
                user_data['region'],
                user_data['city'],
                user_data['link'],
                "",  # Nota removida do cadastro
                image_path,
                user_data['description'],
                message.from_user.username,  # Armazenar o username de quem realizou o cadastro
                ""  # Inicialmente nenhum usuário marcou 'ja_fui'
            )
            
            bot.send_message(message.chat.id, "Peleira cadastrada com sucesso!")
        else:
            bot.send_message(message.chat.id, "Erro ao cadastrar peleira. Tente novamente mais tarde.")
        
        mensagem_inicio(message)
    else:
        bot.send_message(message.chat.id, "Por favor, envie uma imagem para a peleira.")
        bot.register_next_step_handler(message, save_peleira_image)

# A função `mensagem_inicio` deve estar definida em algum lugar do seu código para ser chamada quando o usuário clicar em "Voltar".


#endregion

#region cadastrar encapada
@bot.message_handler(func=lambda message: message.text == 'Cadastrar Peleira')
@restricted
def handle_register_peleira(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn_back)
    bot.send_message(message.chat.id, "Digite o nome da peleira:", reply_markup=markup)
    bot.register_next_step_handler(message, ask_peleira_phone)

def ask_peleira_phone(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    nome = message.text
    if verificar_existencia('name', nome, 'peleiras'):
        bot.send_message(message.chat.id, "Nome já cadastrado. Por favor, insira um nome diferente.")
        bot.register_next_step_handler(message, ask_peleira_phone)
    else:
        user_data['name'] = nome
        bot.send_message(message.chat.id, "Digite o telefone da peleira:")
        bot.register_next_step_handler(message, ask_peleira_value)

def ask_peleira_value(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    telefone = message.text
    if verificar_existencia('phone', telefone, 'peleiras'):
        bot.send_message(message.chat.id, "Telefone já cadastrado. Por favor, insira um telefone diferente.")
        bot.register_next_step_handler(message, ask_peleira_value)
    else:
        user_data['phone'] = telefone
        bot.send_message(message.chat.id, "Digite o valor da peleira:")
        bot.register_next_step_handler(message, ask_peleira_region)

def ask_encapada_region(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['value'] = message.text
    
    markup = types.InlineKeyboardMarkup()
    regions = ["Leste", "Oeste", "Centro", "Sul", "Norte"]

    for region in regions:
        markup.add(types.InlineKeyboardButton(region, callback_data=f"encapada_region_{region}"))
    
    bot.send_message(message.chat.id, "Selecione a região:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('encapada_region_'))
def handle_encapada_region_selection(call):
    region = call.data.split('_')[-1]
    user_data['region'] = region
    
    # Editar a mensagem para remover os botões
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    
    bot.send_message(call.message.chat.id, f"Região selecionada: {region}")
    bot.send_message(call.message.chat.id, "Digite a cidade da encapada:")
    bot.register_next_step_handler(call.message, ask_encapada_city)

def ask_encapada_city(message):
    user_data['city'] = message.text
    bot.send_message(message.chat.id, "Digite o link da encapada:")
    bot.register_next_step_handler(message, ask_encapada_description)

def ask_encapada_description(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['link'] = message.text
    bot.send_message(message.chat.id, "Digite uma breve descrição da encapada:")
    bot.register_next_step_handler(message, ask_encapada_image)

def ask_encapada_image(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return

    user_data['description'] = message.text
    bot.send_message(message.chat.id, "Envie uma imagem para a encapada:")
    bot.register_next_step_handler(message, save_encapada_image)

def save_encapada_image(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return

    if message.photo:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image_name = f"encapada_{user_data['name'].replace(' ', '_')}.jpg"
        image_data = BytesIO(downloaded_file)
        
        image_path = salvar_imagem(image_data, image_name)
        
        if image_path:
            insert_encapada(
                user_data['name'],
                user_data['phone'],
                user_data['value'],
                user_data['region'],
                user_data['city'],
                user_data['link'],
                "",  # Nota removida do cadastro
                image_path,
                user_data['description'],
                message.from_user.username,  # Armazenar o username de quem realizou o cadastro
                ""  # Inicialmente nenhum usuário marcou 'ja_fui'
            )
            
            bot.send_message(message.chat.id, "Encapada cadastrada com sucesso!")
        else:
            bot.send_message(message.chat.id, "Erro ao cadastrar encapada. Tente novamente mais tarde.")
        
        mensagem_inicio(message)
    else:
        bot.send_message(message.chat.id, "Por favor, envie uma imagem para a encapada.")
        bot.register_next_step_handler(message, save_encapada_image)

# Funções de verificação
def verificar_existencia(campo, valor, tabela):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    query = f"SELECT id FROM {tabela} WHERE {campo} = ?"
    cursor.execute(query, (valor,))
    registro = cursor.fetchone()
    conn.close()
    return registro is not None

        
#endregion

#funçao para deletar cadastro de peleiras e encapadas       
#comando para deletar
@bot.message_handler(commands=['deletar_peleira'])
@admin_only
def handle_delete_peleira(message):
    try:
        name = " ".join(message.text.split()[1:])
        if not name:
            raise ValueError("Nome não fornecido")
        delete_peleira(name)
        bot.reply_to(message, f"Peleira '{name}' e seus TDs relacionados foram excluídos com sucesso.")
    except (IndexError, ValueError) as e:
        bot.reply_to(message, f"Erro: {e}\nUso: /deletar_peleira <nome>")
        
@bot.message_handler(commands=['deletar_encapada'])
@admin_only
def handle_delete_encapada(message):
    try:
        name = " ".join(message.text.split()[1:])
        if not name:
            raise ValueError("Nome não fornecido")
        delete_encapada(name)
        bot.reply_to(message, f"Encapada '{name}' e seus TDs relacionados foram excluídos com sucesso.")
    except (IndexError, ValueError) as e:
        bot.reply_to(message, f"Erro: {e}\nUso: /deletar_encapada <nome>")

#region Cadastro de td
@bot.message_handler(func=lambda message: message.text == 'Cadastrar TD')
@restricted
def handle_register_td(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn_back)
    bot.send_message(message.chat.id, "Digite o nome para cadastrar o TD:", reply_markup=markup)
    bot.register_next_step_handler(message, verificar_td_existente)

def verificar_td_existente(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    nome_td = message.text
    if verificar_existencia_registro('peleiras', nome_td) or verificar_existencia_registro('encapadas', nome_td):
        user_data['name'] = nome_td
        bot.send_message(message.chat.id, "Digite o relato para o TD:")
        bot.register_next_step_handler(message, ask_td_report)
    else:
        bot.send_message(message.chat.id, "Nome não encontrado. O cadastro de TD só é permitido para nomes já cadastrados.")
        mensagem_inicio(message)

def ask_td_report(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['report'] = message.text
    bot.send_message(message.chat.id, "Digite a nota para o TD (0 a 10):")
    bot.register_next_step_handler(message, ask_td_score)

def ask_td_score(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    try:
        score = float(message.text.replace(',', '.'))  # Aceita entrada com vírgula ou ponto decimal
        if 0 <= score <= 10:
            user_data['score'] = score
            insert_td(user_data['name'], user_data['report'], message.from_user.username, user_data['score'])
            update_ja_foi(user_data['name'], message.from_user.username, user_data['score'])
            bot.send_message(message.chat.id, "TD cadastrado com sucesso!")
            mensagem_inicio(message)
        else:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "Por favor, insira uma nota válida entre 0 e 10.")
        bot.register_next_step_handler(message, ask_td_score)
#endregion

# Dicionário para armazenar chat_id e message_id da mensagem atual
current_message = {}

#region listar
# Função para listar opções de menu
@bot.message_handler(func=lambda message: message.text == 'Listar')
@restricted
def handle_list_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Listar Peleiras')
    btn2 = types.KeyboardButton('Listar Encapadas')
    btn3 = types.KeyboardButton('Listar TDs')
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn1, btn2, btn3, btn_back)
    bot.send_message(message.chat.id, "Escolha uma opção para listar:", reply_markup=markup)

def get_paginated_peleiras(page, per_page=15):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    offset = (page - 1) * per_page
    cursor.execute('''SELECT * FROM peleiras LIMIT ? OFFSET ?''', (per_page, offset))
    peleiras = cursor.fetchall()
    conn.close()
    return peleiras

# Função para contar o número total de peleiras no banco de dados
def get_peleiras_count():
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT COUNT(*) FROM peleiras''')
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Função para carregar a imagem
def carregar_imagem(image_path):
    try:
        with open(image_path, 'rb') as file:
            return file.read()
    except Exception as e:
        print(f"Erro ao carregar imagem: {e}")
        return None

# Função para enviar peleiras paginadas
def send_peleiras_paginadas(chat_id, page, per_page):
    peleiras = get_paginated_peleiras(page, per_page)
    total_peleiras = get_peleiras_count()
    total_pages = (total_peleiras + per_page - 1) // per_page

    if peleiras:
        for peleira in peleiras:
            image_path = peleira[8]  # O índice 8 corresponde ao caminho da imagem
            image_data = carregar_imagem(image_path)

            if image_data:
                caption = (
                    f"Peleira:\n"
                    f"Nome: {peleira[1]}\n"
                    f"Telefone: {peleira[2]}\n"
                    f"Valor: R${peleira[3]}\n"
                    f"Região: {peleira[4]}\n"
                    f"Cidade: {peleira[5]}\n"
                    f"Link: {peleira[6]}\n"
                    f"Descrição: {peleira[9]}\n"
                    f"Cadastrado por: @{peleira[10]}\n"
                    f"Membros que já foi: {peleira[11]}\n"
                )
                bot.send_photo(chat_id, image_data, caption=caption)
            else:
                bot.send_message(chat_id, "Erro ao baixar imagem da peleira.")

        markup = types.InlineKeyboardMarkup()
        if page > 1:
            markup.add(types.InlineKeyboardButton("⬅️ Anterior", callback_data=f"listar_peleiras_{page-1}"))
        if page < total_pages:
            markup.add(types.InlineKeyboardButton("Próximo ➡️", callback_data=f"listar_peleiras_{page+1}"))

        # Enviar nova mensagem com os botões de navegação
        bot.send_message(chat_id, f"Página {page} de {total_pages}", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Nenhuma peleira encontrada.")

# Manipulador para listar peleiras
@bot.message_handler(func=lambda message: message.text == 'Listar Peleiras')
def handle_list_peleiras(message):
    page = 1  # Primeira página
    per_page = 15  # Registros por página
    send_peleiras_paginadas(message.chat.id, page, per_page)

# Manipulador para callbacks de paginação de peleiras
@bot.callback_query_handler(func=lambda call: call.data.startswith('listar_peleiras_'))
def callback_listar_peleiras(call):
    try:
        page = int(call.data.split('_')[2])  # Pegar o número da página a partir do callback_data
        per_page = 15  # Registros por página
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        # Editar a mensagem anterior para removê-la visualmente
        bot.edit_message_text("Carregando...", chat_id, message_id, reply_markup=None)
        
        # Enviar a nova página de peleiras
        send_peleiras_paginadas(chat_id, page, per_page)
    except IndexError:
        bot.send_message(call.message.chat.id, "Erro ao processar a solicitação de página.")
    except ValueError:
        bot.send_message(call.message.chat.id, "Erro: Página inválida.")
#

def get_paginated_encapadas(page, per_page=15):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    offset = (page - 1) * per_page
    cursor.execute('''SELECT * FROM encapadas LIMIT ? OFFSET ?''', (per_page, offset))
    encapadas = cursor.fetchall()
    conn.close()
    return encapadas

# Função para contar o número total de encapadas no banco de dados
def get_encapadas_count():
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT COUNT(*) FROM encapadas''')
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Função para carregar a imagem
def carregar_imagem(image_path):
    try:
        with open(image_path, 'rb') as file:
            return file.read()
    except Exception as e:
        print(f"Erro ao carregar imagem: {e}")
        return None

# Função para enviar encapadas paginadas
def send_encapadas_paginadas(chat_id, page, per_page):
    encapadas = get_paginated_encapadas(page, per_page)
    total_encapadas = get_encapadas_count()
    total_pages = (total_encapadas + per_page - 1) // per_page

    if encapadas:
        for encapada in encapadas:
            image_path = encapada[8]  # O índice 8 corresponde ao caminho da imagem
            image_data = carregar_imagem(image_path)

            if image_data:
                caption = (
                    f"Encapada:\n"
                    f"Nome: {encapada[1]}\n"
                    f"Telefone: {encapada[2]}\n"
                    f"Valor: R${encapada[3]}\n"
                    f"Região: {encapada[4]}\n"
                    f"Cidade: {encapada[5]}\n"
                    f"Link: {encapada[6]}\n"
                    f"Descrição: {encapada[9]}\n"
                    f"Cadastrado por: @{encapada[10]}\n"
                    f"Membros que já foi: {encapada[11]}\n"
                )
                bot.send_photo(chat_id, image_data, caption=caption)
            else:
                bot.send_message(chat_id, "Erro ao baixar imagem da encapada.")

        markup = types.InlineKeyboardMarkup()
        if page > 1:
            markup.add(types.InlineKeyboardButton("⬅️ Anterior", callback_data=f"listar_encapadas_{page-1}"))
        if page < total_pages:
            markup.add(types.InlineKeyboardButton("Próximo ➡️", callback_data=f"listar_encapadas_{page+1}"))

        # Enviar nova mensagem com os botões de navegação
        bot.send_message(chat_id, f"Página {page} de {total_pages}", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Nenhuma encapada encontrada.")


@bot.message_handler(func=lambda message: message.text == 'Listar TDs')
@restricted

def handle_list_tds(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn_back)
    bot.send_message(message.chat.id, "Digite o nome para buscar TDs:", reply_markup=markup)
    bot.register_next_step_handler(message, list_tds_by_name)

def list_tds_by_name(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    name = message.text
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM tds WHERE name = ?''', (name,))
    tds = cursor.fetchall()
    conn.close()
    caption = "TDs encontrados:"  # Inicializa caption com um valor padrão

    if tds:
        for td in tds:
            caption = f"** TD **\n\n* Nome: {td[1]}\n* Relato: \n{td[2]}\n\n* Realizado por: @{td[3]}\n\n* Nota do TD: {td[4]}"
            caption = escape_markdown(caption)
            bot.send_message(message.chat.id, caption, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "Nenhum TD encontrado para o nome fornecido.")
    
    mensagem_inicio(message)

# Manipulador para listar encapadas
@bot.message_handler(func=lambda message: message.text == 'Listar Encapadas')
def handle_list_encapadas(message):
    page = 1  # Primeira página
    per_page = 15  # Registros por página
    send_encapadas_paginadas(message.chat.id, page, per_page)

# Manipulador para callbacks de paginação de encapadas
@bot.callback_query_handler(func=lambda call: call.data.startswith('listar_encapadas_'))
def callback_listar_encapadas(call):
    try:
        page = int(call.data.split('_')[2])  # Pegar o número da página a partir do callback_data
        per_page = 15  # Registros por página
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        # Editar a mensagem anterior para removê-la visualmente
        bot.edit_message_text("Carregando...", chat_id, message_id, reply_markup=None)
        
        # Enviar a nova página de encapadas
        send_encapadas_paginadas(chat_id, page, per_page)
    except IndexError:
        bot.send_message(call.message.chat.id, "Erro ao processar a solicitação de página.")
    except ValueError:
        bot.send_message(call.message.chat.id, "Erro: Página inválida.")
#endregion listar

#region menu buscar
@bot.message_handler(func=lambda message: message.text == 'Buscar')
@restricted

def menu_busca(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Buscar por Nome')
    btn2 = types.KeyboardButton('Buscar por Região')
    btn3 = types.KeyboardButton('Buscar por Cidade')
    btn4 = types.KeyboardButton('Buscar por Número')
    btn5 = types.KeyboardButton('Buscar por Valor Médio')
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn_back)
    bot.send_message(message.chat.id, "Escolha uma opção de busca:", reply_markup=markup)

#busca por nome
@bot.message_handler(func=lambda message: message.text == 'Buscar por Nome')
@restricted

def handle_search_by_name(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn_back)
    bot.send_message(message.chat.id, "Digite o nome para buscar:", reply_markup=markup)
    bot.register_next_step_handler(message, search_by_name)

def search_by_name(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    name = message.text
    peleiras, encapadas = search_peleiras_and_encapadas_by_name(name)
    
    for peleira in peleiras:
        image_path = peleira[8]  # O índice 8 corresponde ao caminho da imagem
        image_data = carregar_imagem(image_path)
        
        
        if image_data:
            caption = (
                  f"** Peleira **\n\n"
                f"* Nome:  {peleira[1]}\n"
                f"* Telefone:  {peleira[2]}\n"
                f"* Valor:  R${peleira[3]}\n"
                f"* Região:  {peleira[4]}\n"
                f"* Cidade:  {peleira[5]}\n"
                f"* Link:  {peleira[6]}\n"
                f"* Descrição:  *{peleira[9]}\n"
                f"* Cadastrado por: \n@{peleira[10]}\n"
                f"* Membros que já foi:\n{peleira[11]}\n"  # Adicionado o nome do usuário que já foi
                )
            caption = escape_markdown(caption)
            bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Erro ao baixar imagem da peleira.")

    for encapada in encapadas:
        image_path = encapada[8]  # O índice 8 corresponde ao caminho da imagem
        image_data = carregar_imagem(image_path)
        
        if image_data:
            caption = (
               f"** Encapada **\n\n"
                f"* Nome:  {encapada[1]}\n"
                f"* Telefone:  {encapada[2]}\n"
                f"* Valor:  R${encapada[3]}\n"
                f"* Região:  {encapada[4]}\n"
                f"* Cidade:  {encapada[5]}\n"
                f"* Link:  {encapada[6]}\n"
                f"* Descrição:  *{encapada[9]}\n\n"
                f"* Cadastrado por:  \n@{encapada[10]}\n"
                f"* Membros que já foi: \n{encapada[11]}"  # Adicionado o nome do usuário que já foi
            )
            
            caption = escape_markdown(caption)
            bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Erro ao baixar imagem da encapada.")
      
    mensagem_inicio(message)

#Busca por regiao 
@bot.message_handler(func=lambda message: message.text == 'Buscar por Região')
@restricted

def handle_search_by_region(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Norte')
    btn2 = types.KeyboardButton('Sul')
    btn3 = types.KeyboardButton('Leste')
    btn4 = types.KeyboardButton('Oeste')
    btn5 = types.KeyboardButton('Centro')
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn_back)
    bot.send_message(message.chat.id, "Escolha a região para buscar:", reply_markup=markup)
    bot.register_next_step_handler(message, search_by_region)

def search_by_region(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    region = message.text
    peleiras, encapadas = search_peleiras_and_encapadas_by_region(region)

    for peleira in peleiras:
        image_path = peleira[8]  # O índice 8 corresponde ao caminho da imagem
        image_data = carregar_imagem(image_path)
        
        
        if image_data:
            caption = (
                  f"** Peleira **\n\n"
                f"* Nome:  {peleira[1]}\n"
                f"* Telefone:  {peleira[2]}\n"
                f"* Valor:  R${peleira[3]}\n"
                f"* Região:  {peleira[4]}\n"
                f"* Cidade:  {peleira[5]}\n"
                f"* Link:  {peleira[6]}\n"
                f"* Descrição:  *{peleira[9]}\n"
                f"* Cadastrado por: \n@{peleira[10]}\n"
                f"* Membros que já foi:\n{peleira[11]}\n"  # Adicionado o nome do usuário que já foi
                )
            caption = escape_markdown(caption)
            bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Erro ao baixar imagem da peleira.")

    for encapada in encapadas:
        image_path = encapada[8]  # O índice 8 corresponde ao caminho da imagem
        image_data = carregar_imagem(image_path)
        
        if image_data:
            caption = (
               f"** Encapada **\n\n"
                f"* Nome:  {encapada[1]}\n"
                f"* Telefone:  {encapada[2]}\n"
                f"* Valor:  R${encapada[3]}\n"
                f"* Região:  {encapada[4]}\n"
                f"* Cidade:  {encapada[5]}\n"
                f"* Link:  {encapada[6]}\n"
                f"* Descrição:  *{encapada[9]}\n\n"
                f"* Cadastrado por:  \n@{encapada[10]}\n"
                f"* Membros que já foi: \n{encapada[11]}"  # Adicionado o nome do usuário que já foi
            )
            
            caption = escape_markdown(caption)
            bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Erro ao baixar imagem da encapada.")
      
    mensagem_inicio(message)

#busca por cidade
@bot.message_handler(func=lambda message: message.text == 'Buscar por Cidade')
@restricted

def handle_search_by_address(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn_back)
    bot.send_message(message.chat.id, "Digite o endereço para buscar:", reply_markup=markup)
    bot.register_next_step_handler(message, search_by_address)

def search_by_address(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    address = message.text
    peleiras, encapadas = search_peleiras_and_encapadas_by_address(address)

    for peleira in peleiras:
        image_path = peleira[8]  # O índice 8 corresponde ao caminho da imagem
        image_data = carregar_imagem(image_path)
        
        if image_data:
            caption = (
                  f"** Peleira **\n\n"
                f"* Nome:  {peleira[1]}\n"
                f"* Telefone:  {peleira[2]}\n"
                f"* Valor:  R${peleira[3]}\n"
                f"* Região:  {peleira[4]}\n"
                f"* Cidade:  {peleira[5]}\n"
                f"* Link:  {peleira[6]}\n"
                f"* Descrição:  *{peleira[9]}\n"
                f"* Cadastrado por: \n@{peleira[10]}\n"
                f"* Membros que já foi:\n{peleira[11]}\n"  # Adicionado o nome do usuário que já foi
                )
            caption = escape_markdown(caption)
            bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Erro ao baixar imagem da peleira.")

    for encapada in encapadas:
        image_path = encapada[8]  # O índice 8 corresponde ao caminho da imagem
        image_data = carregar_imagem(image_path)
        
        if image_data:
            caption = (
               f"** Encapada **\n\n"
                f"* Nome:  {encapada[1]}\n"
                f"* Telefone:  {encapada[2]}\n"
                f"* Valor:  R${encapada[3]}\n"
                f"* Região:  {encapada[4]}\n"
                f"* Cidade:  {encapada[5]}\n"
                f"* Link:  {encapada[6]}\n"
                f"* Descrição:  *{encapada[9]}\n\n"
                f"* Cadastrado por:  \n@{encapada[10]}\n"
                f"* Membros que já foi: \n{encapada[11]}"  # Adicionado o nome do usuário que já foi
            )
            
            caption = escape_markdown(caption)
            bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Erro ao baixar imagem da encapada.")
      
    mensagem_inicio(message)

#busca por numero de telefone
@bot.message_handler(func=lambda message: message.text == 'Buscar por Número')
@restricted

def handle_search_by_phone(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn_back)
    bot.send_message(message.chat.id, "Digite o número para buscar:", reply_markup=markup)
    bot.register_next_step_handler(message, search_by_phone)

def search_by_phone(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    phone = message.text
    peleiras, encapadas = search_peleiras_and_encapadas_by_phone(phone)

    for peleira in peleiras:
        image_path = peleira[8]  # O índice 8 corresponde ao caminho da imagem
        image_data = carregar_imagem(image_path)
        
        if image_data:
            caption = (
                  f"** Peleira **\n\n"
                f"* Nome:  {peleira[1]}\n"
                f"* Telefone:  {peleira[2]}\n"
                f"* Valor:  R${peleira[3]}\n"
                f"* Região:  {peleira[4]}\n"
                f"* Cidade:  {peleira[5]}\n"
                f"* Link:  {peleira[6]}\n"
                f"* Descrição:  *{peleira[9]}\n"
                f"* Cadastrado por: \n@{peleira[10]}\n"
                f"* Membros que já foi:\n{peleira[11]}\n"  # Adicionado o nome do usuário que já foi
                )
            caption = escape_markdown(caption)
            bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Erro ao baixar imagem da peleira.")

    for encapada in encapadas:
        image_path = encapada[8]  # O índice 8 corresponde ao caminho da imagem
        image_data = carregar_imagem(image_path)
        if image_data:
            caption = (
               f"** Encapada **\n\n"
                f"* Nome:  {encapada[1]}\n"
                f"* Telefone:  {encapada[2]}\n"
                f"* Valor:  R${encapada[3]}\n"
                f"* Região:  {encapada[4]}\n"
                f"* Cidade:  {encapada[5]}\n"
                f"* Link:  {encapada[6]}\n"
                f"* Descrição:  *{encapada[9]}\n\n"
                f"* Cadastrado por:  \n@{encapada[10]}\n"
                f"* Membros que já foi: \n{encapada[11]}"  # Adicionado o nome do usuário que já foi
            )
            
            caption = escape_markdown(caption)
            bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Erro ao baixar imagem da encapada.")
      
    mensagem_inicio(message)
    
#bucar por valor médio
@bot.message_handler(func=lambda message: message.text == 'Buscar por Valor Médio')
@restricted

def handle_search_by_value(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn_back)
    bot.send_message(message.chat.id, "Digite o valor médio para buscar:", reply_markup=markup)
    bot.register_next_step_handler(message, search_by_value)

def search_by_value(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    
    value = message.text
    peleiras, encapadas = search_peleiras_and_encapadas_by_value(value)
    
    for peleira in peleiras:
        image_path = peleira[8]  # O índice 8 corresponde ao caminho da imagem
        image_data = carregar_imagem(image_path)
        
        if image_data:
            caption = (
                  f"** Peleira **\n\n"
                f"* Nome:  {peleira[1]}\n"
                f"* Telefone:  {peleira[2]}\n"
                f"* Valor:  R${peleira[3]}\n"
                f"* Região:  {peleira[4]}\n"
                f"* Cidade:  {peleira[5]}\n"
                f"* Link:  {peleira[6]}\n"
                f"* Descrição:  *{peleira[9]}\n"
                f"* Cadastrado por: \n@{peleira[10]}\n"
                f"* Membros que já foi:\n{peleira[11]}\n"  # Adicionado o nome do usuário que já foi
                )
            caption = escape_markdown(caption)
            bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Erro ao baixar imagem da peleira.")

    for encapada in encapadas:
        image_path = encapada[8]  # O índice 8 corresponde ao caminho da imagem
        image_data = carregar_imagem(image_path)
        
        if image_data:
            caption = (
               f"** Encapada **\n\n"
                f"* Nome:  {encapada[1]}\n"
                f"* Telefone:  {encapada[2]}\n"
                f"* Valor:  R${encapada[3]}\n"
                f"* Região:  {encapada[4]}\n"
                f"* Cidade:  {encapada[5]}\n"
                f"* Link:  {encapada[6]}\n"
                f"* Descrição:  *{encapada[9]}\n\n"
                f"* Cadastrado por:  \n@{encapada[10]}\n"
                f"* Membros que já foi: \n{encapada[11]}"  # Adicionado o nome do usuário que já foi
            )
            
            caption = escape_markdown(caption)
            bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Erro ao baixar imagem da encapada.")
      
    mensagem_inicio(message)
#endregion

#region funçao de busca no banco de dados para menu de busca
def search_peleiras_and_encapadas_by_name(name):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM peleiras WHERE name = ?''', (name,))
    peleiras = cursor.fetchall()
    cursor.execute('''SELECT * FROM encapadas WHERE name = ?''', (name,))
    encapadas = cursor.fetchall()
    conn.close()
    return peleiras, encapadas

def search_peleiras_and_encapadas_by_region(region):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM peleiras WHERE region = ?''', (region,))
    peleiras = cursor.fetchall()
    cursor.execute('''SELECT * FROM encapadas WHERE region = ?''', (region,))
    encapadas = cursor.fetchall()
    conn.close()
    return peleiras, encapadas

def search_peleiras_and_encapadas_by_address(address):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM peleiras WHERE city = ?''', (address,))
    peleiras = cursor.fetchall()
    cursor.execute('''SELECT * FROM encapadas WHERE city = ?''', (address,))
    encapadas = cursor.fetchall()
    conn.close()
    return peleiras, encapadas

def search_peleiras_and_encapadas_by_phone(phone):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM peleiras WHERE phone = ?''', (phone,))
    peleiras = cursor.fetchall()
    cursor.execute('''SELECT * FROM encapadas WHERE phone = ?''', (phone,))
    encapadas = cursor.fetchall()
    conn.close()
    return peleiras, encapadas

def search_peleiras_and_encapadas_by_value(value):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM peleiras WHERE value = ?''', (value,))
    peleiras = cursor.fetchall()
    cursor.execute('''SELECT * FROM encapadas WHERE value = ?''', (value,))
    encapadas = cursor.fetchall()
    conn.close()
    return peleiras, encapadas
#endregion

if __name__ == '__main__':
    bot.polling(none_stop=True)
