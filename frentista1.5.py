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
                        score INTEGER,
                        image TEXT,
                        username TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS encapadas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        phone TEXT,
                        value TEXT,
                        region TEXT,
                        city TEXT,
                        link TEXT,
                        score INTEGER,
                        image TEXT,
                        username TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tds (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        report TEXT,
                        username TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuario_permitido 
    (username TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

# Cria o banco de dados ao iniciar o script
create_database()

#Funções para Gerenciar Usuários Permitidos. Adicione funções para adicionar, remover e verificar usuários permitidos
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

#Decorador para Restringir Acesso Adicione um decorator para restringir o acesso a comandos e funções específicas

usuario_adm = 5493230042  # Substitua pelo seu ID de usuário do Telegram

def admin_only(func):
    def wrapper(message):
        if message.from_user.id == usuario_adm:
            return func(message)
        else:
            bot.reply_to(message, "Apenas administradores podem executar este comando.")
    return wrapper

def restricted(func):
    def wrapper(message):
        if usuario_permitido(message.from_user.username) or message.from_user.id == usuario_adm:
            return func(message)
        else:
            bot.reply_to(message, "Você não tem permissão para usar este bot.")
    return wrapper  



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

def insert_peleira(name, phone, value, region, city, link, score, image, username):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO peleiras (name, phone, value, region, city, link, score, image, username)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (name, phone, value, region, city, link, score, image, username))
    conn.commit()
    conn.close()

def insert_encapada(name, phone, value, region, city, link, score, image, username):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO encapadas (name, phone, value, region, city, link, score, image, username)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (name, phone, value, region, city, link, score, image, username))
    conn.commit()
    conn.close()

def insert_td(name, report, username):
    conn = sqlite3.connect('frentistas_bot.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO tds (name, report, username) VALUES (?, ?, ?)''', (name, report, username))
    conn.commit()
    conn.close()

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

import re
def escape_markdown(text):
    escape_chars = r'\*_`['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)

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
    bot.send_message(message.chat.id, "Digite a região da peleira:")
    bot.register_next_step_handler(message, ask_peleira_city)

def ask_peleira_city(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['region'] = message.text
    bot.send_message(message.chat.id, "Digite a cidade da peleira:")
    bot.register_next_step_handler(message, ask_peleira_link)

def ask_peleira_link(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['city'] = message.text
    bot.send_message(message.chat.id, "Digite o link da peleira:")
    bot.register_next_step_handler(message, ask_peleira_score)

def ask_peleira_score(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['link'] = message.text
    bot.send_message(message.chat.id, "Digite a nota da peleira (0 a 10):")
    bot.register_next_step_handler(message, ask_peleira_image)

def ask_peleira_image(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['score'] = int(message.text)
    msg = bot.send_message(message.chat.id, "Envie uma imagem para a peleira:")
    bot.register_next_step_handler(msg, save_peleira_image)


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
                user_data['score'],
                image_path,
                message.from_user.username  # Armazenar o username de quem realizou o cadastro
            )
            
            bot.send_message(message.chat.id, "Peleira cadastrada com sucesso!")
        else:
            bot.send_message(message.chat.id, "Erro ao cadastrar peleira. Tente novamente mais tarde.")
        
        mensagem_inicio(message)

@bot.message_handler(func=lambda message: message.text == 'Cadastrar Encapada')
@restricted

def handle_register_encapada(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn_back)
    bot.send_message(message.chat.id, "Digite o nome da encapada:", reply_markup=markup)
    bot.register_next_step_handler(message, ask_encapada_phone)

def ask_encapada_phone(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['name'] = message.text
    bot.send_message(message.chat.id, "Digite o telefone da encapada:")
    bot.register_next_step_handler(message, ask_encapada_value)

def ask_encapada_value(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['phone'] = message.text
    bot.send_message(message.chat.id, "Digite o valor da encapada:")
    bot.register_next_step_handler(message, ask_encapada_region)

def ask_encapada_region(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['value'] = message.text
    bot.send_message(message.chat.id, "Digite a região da encapada:")
    bot.register_next_step_handler(message, ask_encapada_city)

def ask_encapada_city(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['region'] = message.text
    bot.send_message(message.chat.id, "Digite a cidade da encapada:")
    bot.register_next_step_handler(message, ask_encapada_link)

def ask_encapada_link(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['city'] = message.text
    bot.send_message(message.chat.id, "Digite o link da encapada:")
    bot.register_next_step_handler(message, ask_encapada_score)

def ask_encapada_score(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['link'] = message.text
    bot.send_message(message.chat.id, "Digite a nota da encapada (0 a 10):")
    bot.register_next_step_handler(message, ask_encapada_image)

def ask_encapada_image(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['score'] = int(message.text)
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
                user_data['score'],
                image_path,
                message.from_user.username  # Armazenar o username de quem realizou o cadastro
            )
            
            bot.send_message(message.chat.id, "Encapada cadastrada com sucesso!")
        else:
            bot.send_message(message.chat.id, "Erro ao cadastrar encapada. Tente novamente mais tarde.")
        
        mensagem_inicio(message)

 #funçao para deletar cadastro de peleiras e encapadas       

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

@bot.message_handler(func=lambda message: message.text == 'Cadastrar TD')
@restricted
def handle_register_td(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    btn_back = types.KeyboardButton('Voltar')
    markup.add(btn_back)
    bot.send_message(message.chat.id, "Digite o nome para cadastrar o TD:", reply_markup=markup)
    bot.register_next_step_handler(message, ask_td_report)

def ask_td_report(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['name'] = message.text
    bot.send_message(message.chat.id, "Digite o relato para o TD:")
    bot.register_next_step_handler(message, save_td_report)

def save_td_report(message):
    if message.text == 'Voltar':
        mensagem_inicio(message)
        return
    user_data['report'] = message.text
    insert_td(user_data['name'], user_data['report'], message.from_user.username)
    bot.send_message(message.chat.id, "TD cadastrado com sucesso!")
    mensagem_inicio(message)

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

@bot.message_handler(func=lambda message: message.text == 'Listar Peleiras')
@restricted

def handle_list_peleiras(message):
    peleiras = list_peleiras()
    
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
                f"* Nota:  {peleira[7]}\n"
                f"* Cadastrado por:  @{peleira[9]}"
                )
                caption = escape_markdown(caption)
                bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
            else:
                 bot.send_message(message.chat.id, "Erro ao baixar imagem da peleira.")
    
    mensagem_inicio(message)

@bot.message_handler(func=lambda message: message.text == 'Listar Encapadas')
@restricted

def handle_list_encapadas(message):
    encapadas = list_encapadas()
    
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
                f"* Nota:  {encapada[7]}\n"
                f"* Cadastrado por:  @{encapada[9]}"
            )
            
            caption = escape_markdown(caption)
            bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Erro ao baixar imagem da encapada.")
    
    mensagem_inicio(message)

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
            caption = f"** TD **\n\n* Nome: {td[1]}\n* Relato: \n{td[2]}\n\n* Realizado por: @{td[3]}"
            caption = escape_markdown(caption)
            bot.send_message(message.chat.id, caption, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "Nenhum TD encontrado para o nome fornecido.")
    
    mensagem_inicio(message)

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
                f"* Nota:  {peleira[7]}\n"
                f"* Cadastrado por:  @{peleira[9]}"
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
                f"* Nota:  {encapada[7]}\n"
                f"* Cadastrado por:  @{encapada[9]}"
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
                f"* Nota:  {peleira[7]}\n"
                f"* Cadastrado por:  @{peleira[9]}"
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
                f"* Nota:  {encapada[7]}\n"
                f"* Cadastrado por:  @{encapada[9]}"
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
                f"* Nota:  {peleira[7]}\n"
                f"* Cadastrado por:  @{peleira[9]}"
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
                f"* Nota:  {encapada[7]}\n"
                f"* Cadastrado por:  @{encapada[9]}"
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
                f"* Nota:  {peleira[7]}\n"
                f"* Cadastrado por:  @{peleira[9]}"
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
                f"* Nota:  {encapada[7]}\n"
                f"* Cadastrado por:  @{encapada[9]}"
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
                f"* Nota:  {peleira[7]}\n"
                f"* Cadastrado por:  @{peleira[9]}"
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
                f"* Nota:  {encapada[7]}\n"
                f"* Cadastrado por:  @{encapada[9]}"
            )
            
            caption = escape_markdown(caption)
            bot.send_photo(message.chat.id, image_data, caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Erro ao baixar imagem da encapada.")
      
    mensagem_inicio(message)

# Helper functions for search
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

if __name__ == '__main__':
    bot.polling(none_stop=True)
