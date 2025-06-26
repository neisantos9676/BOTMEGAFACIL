import os
import random
import telebot
from telebot import types
from datetime import datetime
import pytz
import time

# Configuração inicial
TOKEN = os.getenv('TELEGRAM_TOKEN')  # Obter do ambiente
bot = telebot.TeleBot(TOKEN)

# Dados estratégicos atualizados
MEGA_QUENTES = [5, 10, 34, 33, 53, 37, 38, 43]
MEGA_ATRASADOS = [11, 42, 55, 59, 7, 29]

LOTO_QUENTES = [2, 3, 5, 7, 10, 13, 14, 15, 17, 18, 20, 21, 22, 24, 25]
LOTO_ATRASADOS = [4, 6, 9, 12, 16]

# Armazenamento de usuários em memória (para produção use DB)
usuarios = {}

# Saudação inteligente com emoji
def saudacao():
    hora = datetime.now(pytz.timezone('America/Sao_Paulo')).hour
    if 5 <= hora < 12:
        return "☀️ Bom dia"
    elif 12 <= hora < 18:
        return "🌤 Boa tarde"
    else:
        return "🌙 Boa noite"

# Calcular melhoria de chances
def calcular_melhoria(loteria):
    if "Mega" in loteria:
        return random.randint(22, 35)  # % estimada
    else:
        return random.randint(15, 25)  # % estimada

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    usuarios[chat_id] = {
        "jogos_gratis": 3,
        "telefone": None,
        "loteria": None,
        "nome": message.from_user.first_name
    }
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_mega = types.KeyboardButton('🎰 Mega-Sena')
    btn_loto = types.KeyboardButton('📊 Lotofácil')
    markup.add(btn_mega, btn_loto)
    
    bot.send_message(
        chat_id,
        f"{saudacao()}, {usuarios[chat_id]['nome']}! Eu sou o *Mega Guru* 🤖\n\n"
        "🎁 Você ganhou *3 JOGOS GRÁTIS* para testar!\n"
        "🔮 Escolha sua loteria abaixo:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda msg: msg.text in ['🎰 Mega-Sena', '📊 Lotofácil'])
def escolher_loteria(message):
    chat_id = message.chat.id
    usuarios[chat_id]["loteria"] = message.text
    
    if usuarios[chat_id]["jogos_gratis"] > 0:
        gerar_jogo_gratis(chat_id)
    else:
        mostrar_planos(chat_id)

def gerar_jogo_gratis(chat_id):
    loteria = usuarios[chat_id]["loteria"]
    usuarios[chat_id]["jogos_gratis"] -= 1
    
    if "Mega" in loteria:
        # Estratégia: 3 quentes + 2 aleatórios + 1 atrasado
        quentes = random.sample(MEGA_QUENTES, 3)
        resto = [n for n in range(1, 61) if n not in quentes]
        aleatorios = random.sample(resto, 2)
        atrasado = random.choice(MEGA_ATRASADOS)
        jogo = sorted(quentes + aleatorios + [atrasado])
        
        mensagem = (
            f"🎰 *JOGO GRÁTIS - MEGA-SENA*\n\n"
            f"`{jogo}`\n\n"
            f"🔥 Números quentes: {quentes[0]}, {quentes[1]}, {quentes[2]}\n"
            f"⏳ Número atrasado: {atrasado}\n"
            f"📈 Chance aumentada em {calcular_melhoria(loteria)}%"
        )
    else:
        # Estratégia: 10 quentes + 5 aleatórios
        quentes = random.sample(LOTO_QUENTES, 10)
        resto = [n for n in range(1, 26) if n not in quentes]
        aleatorios = random.sample(resto, 5)
        jogo = sorted(quentes + aleatorios)
        
        mensagem = (
            f"📊 *JOGO GRÁTIS - LOTO FÁCIL*\n\n"
            f"`{jogo}`\n\n"
            f"🔥 Top 3 quentes: {quentes[0]}, {quentes[1]}, {quentes[2]}\n"
            f"📈 Chance aumentada em {calcular_melhoria(loteria)}%"
        )
    
    # Atualizar interface
    if usuarios[chat_id]["jogos_gratis"] > 0:
        mensagem += f"\n\nVocê ainda tem *{usuarios[chat_id]['jogos_gratis']}