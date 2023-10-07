import logging
from dotenv import load_dotenv
import telebot
import openai
from telebot import types
import requests
from bs4 import BeautifulSoup
from decouple import config

# Inisialisasi logger dan muat variabel lingkungan
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
load_dotenv()

# Inisialisasi bot dan kunci API OpenAI
bot = telebot.TeleBot(config("BOT_API_KEY"))
openai.api_key = config("OPENAI_API_KEY")

# Daftar perintah bot
commands = [
        types.BotCommand("start", "Mulai percakapan dengan bot"),
        types.BotCommand("help", "Tampilkan bantuan dan perintah"),
        types.BotCommand("author", "Tampilkan informasi penulis bot"),
        types.BotCommand("about", "Tentang bot OpenAI"),
        types.BotCommand("question", "Ajukan pertanyaan kepada bot"),
        types.BotCommand("chat", "Mulai percakapan dengan bot"),
        types.BotCommand("summary", "Ringkas teks yang diberikan"),
        types.BotCommand("translate", "Terjemahkan teks yang diberikan"),
        types.BotCommand("analyze", "Analisis teks yang diberikan"),
    ]

# Fungsi untuk melakukan pencarian di Google
def search_google(query):
    google_api_key = config("YOUR_GOOGLE_API_KEY")
    search_engine_id = config("YOUR_CUSTOM_SEARCH_ENGINE_ID")
    url = f"https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        if "items" in data:
            search_results = data["items"]
            return search_results
        else:
            return []

    except Exception as e:
        logging.error("Error searching Google:", e)
        return []

# Fungsi untuk mengirim pesan panjang ke pengguna
def send_long_message(chat_id, text):
    # Batasan panjang pesan Telegram
    max_message_length = 4096

    # Memeriksa apakah teks terlalu panjang
    if len(text) <= max_message_length:
        # Jika teks cukup pendek, kirim langsung
        bot.send_message(chat_id, text)
    else:
        # Jika teks terlalu panjang, bagi menjadi pesan-pesan yang lebih kecil
        while text:
            # Bagi teks menjadi potongan maksimum
            message_chunk = text[:max_message_length]
            text = text[max_message_length:]

            # Kirim potongan pesan
            bot.send_message(chat_id, message_chunk)

# Fungsi untuk menjawab pertanyaan pengguna
def answer_question(user_question):
    search_results = search_google(user_question)
    
    if search_results:
        # Pilih hasil pertama sebagai link
        first_result = search_results[0]["link"]
        
        # Lakukan permintaan HTTP untuk mengambil halaman web
        try:
            response = requests.get(first_result)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Parse halaman web menggunakan BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ambil teks dari halaman web (misalnya, dari elemen <p>)
            text_from_page = ""
            for paragraph in soup.find_all('p'):
                text_from_page += paragraph.text
            
            # Proses teks untuk menghasilkan jawaban yang relevan
            # Misalnya, Anda bisa menggunakan pemotongan teks atau pemrosesan NLP
            # Di sini, kami hanya akan mengambil beberapa karakter pertama sebagai contoh
            answer = text_from_page[:200]  # Ambil 200 karakter pertama
            
            return answer
        except Exception as e:
            print("Error retrieving and processing web page:", e)
    
    return "Maaf, saya tidak dapat menemukan jawaban untuk pertanyaan Anda."

# Mengatur perintah-perintah bot
bot.set_my_commands(commands)

# Handler untuk perintah /start
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.username
    bot.send_message(message.chat.id, f"Hello {user_name}, selamat datang di ChatBot OpenAI. Temui teman AI Anda - bot OpenAI! Dengan teknologi AI terkini, saya di sini untuk menjawab pertanyaan, membantu dalam tugas, dan memberikan solusi kreatif. Mulai dari riset hingga percakapan santai, saya adalah asisten virtual pintar Anda, siap untuk berinteraksi, belajar, dan menginspirasi. Mari kita eksplorasi dunia AI bersama!")

# Handler untuk perintah /help
@bot.message_handler(commands=['help'])
def help(message):
    user_message = message.text.lower()
    response = "Silakan gunakan perintah berikut:\n\n"
    
    if "bantuan" in user_message:
        response += "Saya bisa memberikan bantuan. Silakan ajukan pertanyaan atau permintaan Anda."
    elif "fitur" in user_message:
        response += "Berikut adalah beberapa fitur yang dapat Anda gunakan:\n"
        response += "- Ketik /start untuk memulai percakapan dengan bot.\n"
        response += "- Ketik /author untuk mengetahui penulis bot ini.\n"
        response += "- Ketik /about untuk informasi lebih lanjut tentang bot ini.\n"
    else:
        response += "Maaf, saya tidak mengenali permintaan Anda. Silakan ketik /help untuk melihat daftar perintah yang tersedia."

    bot.send_message(message.chat.id, response)

# Handler untuk perintah /question
@bot.message_handler(commands=['question'])
def handle_question(message):
    user_question = message.text[10:]
    
    if user_question:
        response = answer_question(user_question)
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Silakan ajukan pertanyaan Anda setelah perintah /question.")

# Handler untuk perintah /chat
@bot.message_handler(commands=['chat'])
def handle_chat(message):
    bot.send_message(message.chat.id, "Anda bisa mulai berbicara dengan saya sekarang.")

# Handler untuk perintah /summary
@bot.message_handler(commands=['summary'])
def handle_summary(message):
    bot.send_message(message.chat.id, "Berikan teks yang ingin Anda ringkas.")

# Handler untuk perintah /translate
@bot.message_handler(commands=['translate'])
def handle_translate(message):
    bot.send_message(message.chat.id, "Berikan teks yang ingin Anda terjemahkan.")

# Handler untuk perintah /analyze
@bot.message_handler(commands=['analyze'])
def handle_analyze(message):
    bot.send_message(message.chat.id, "Berikan teks yang ingin Anda analisis.")

# Handler untuk perintah /author
@bot.message_handler(commands=['author'])
def author(message):
    bot.send_message(message.chat.id, "Bot ini dikembangkan oleh @SiberWise atau nama aslinya adalah Dearly Febriano Irwansyah.")

# Handler untuk perintah /about
@bot.message_handler(commands=['about'])
def about(message):
    bot.send_message(message.chat.id, "Temui teman AI Anda - bot OpenAI! Dengan teknologi AI terkini, saya di sini untuk menjawab pertanyaan, membantu dalam tugas, dan memberikan solusi kreatif. Mulai dari riset hingga percakapan santai, saya adalah asisten virtual pintar Anda, siap untuk berinteraksi, belajar, dan menginspirasi. Mari kita eksplorasi dunia AI bersama!")

# Handler untuk pesan selain perintah
@bot.message_handler(func=lambda message: True)
def get_response(message):
    user_name = message.from_user.username
    response = f"Hello {user_name}, selamat datang di ChatBot OpenAI. Temui teman AI Anda - bot OpenAI! Dengan teknologi AI terkini, saya di sini untuk menjawab pertanyaan, membantu dalam tugas, dan memberikan solusi kreatif. Mulai dari riset hingga percakapan santai, saya adalah asisten virtual pintar Anda, siap untuk berinteraksi, belajar, dan menginspirasi. Mari kita eksplorasi dunia AI bersama! "
    if message.text.startswith(">>>"):
        response = openai.Completion.create(
            engine="code-davinci-002",
            prompt=f'```\n{message.text[3:]}\n```',
            temperature=0,
            max_tokens=4000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n", ">>>"],
        )
    else:
        if "code" in message.text.lower() or "python" in message.text.lower():
            response = openai.Completion.create(
                engine="code-davinci-002",
                prompt=f'"""\n{message.text}\n"""',
                temperature=0,
                max_tokens=4000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=['"""'],
            )
        else:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f'"""\n{message.text}\n"""',
                temperature=0,
                max_tokens=2000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=['"""'],
            )

    bot.send_message(message.chat.id, f'{response["choices"][0]["text"]}', parse_mode="None")

# Jalankan bot secara terus-menerus
bot.infinity_polling()
