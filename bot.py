import logging
import random
import json
import csv
import io
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# CONFIGURA TU TOKEN AQUÍ (línea 11)
TOKEN = "8087989542:AAGRb-mmNl5B5J0nCdxGrhPwg1V_4TWt7FY"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class NamsoGen:
    def __init__(self):
        self.cards = []
    
    def luhn_checksum(self, num):
        digits = [int(d) for d in str(num)]
        checksum = 0
        for i, d in enumerate(reversed(digits)):
            if i % 2 == 0:
                d *= 2
                if d > 9:
                    d -= 9
            checksum += d
        return checksum % 10
    
    def generate_card(self, bin_input, length=16):
        prefix = "".join(str(random.randint(0,9)) if c.upper()=='X' else c for c in bin_input)
        number = prefix
        while len(number) < length - 1:
            number += str(random.randint(0, 9))
        checksum = sum(int(d) for d in str(self.luhn_checksum(int(number)*10)))
        check_digit = (10 - checksum) % 10
        return int(number + str(check_digit))
    
    def generate_full(self, bin_input, qty=10):
        self.cards = []
        length = 15 if bin_input.startswith('3') else 16
        for _ in range(qty):
            num = self.generate_card(bin_input, length)
            month = str(random.randint(1,12)).zfill(2)
            year = str(random.randint(25,30))
            cvv_len = 4 if bin_input.startswith('3') else 3
            cvv = str(random.randint(0, 10**cvv_len-1)).zfill(cvv_len)
            self.cards.append({
                'number': str(num), 'month': month, 
                'year': year, 'cvv': cvv
            })
        return self.cards
    
    def to_txt(self):
        return '\n'.join(f"{c['number']}|{c['month']}|{c['year']}|{c['cvv']}" for c in self.cards)

namso = NamsoGen()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎴 *Namso Gen Bot*\n\n"
        "Comandos:\n"
        "/gen `<BIN>` `<cantidad>` - Generar tarjetas\n"
        "/export - Descargar archivo\n\n"
        "Ejemplo: `/gen 411111 10`",
        parse_mode='Markdown'
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("❌ Usa: /gen `<BIN>` `<cantidad>`", parse_mode='Markdown')
        return
    
    bin_input = context.args[0]
    qty = int(context.args[1]) if len(context.args) > 1 else 10
    if qty > 100:
        qty = 100
    
    await update.message.reply_text(f"⏳ Generando {qty} tarjetas...")
    
    namso.generate_full(bin_input, qty)
    
    # Mostrar preview
    preview = "🎴 *Tarjetas generadas:*\n\n"
    for c in namso.cards[:5]:
        preview += f"`{c['number']}`\n📅 {c['month']}/{c['year']} 🔒 `{c['cvv']}`\n\n"
    if len(namso.cards) > 5:
        preview += f"...y {len(namso.cards)-5} más\n"
    
    await update.message.reply_text(preview, parse_mode='Markdown')
    
    # Enviar archivo
    txt = namso.to_txt()
    await update.message.reply_document(
        document=io.BytesIO(txt.encode()),
        filename=f"cards_{bin_input}.txt"
    )

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not namso.cards:
        await update.message.reply_text("❌ Primero genera tarjetas con /gen")
        return
    txt = namso.to_txt()
    await update.message.reply_document(
        document=io.BytesIO(txt.encode()),
        filename="tarjetas_export.txt"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", generate))
    app.add_handler(CommandHandler("export", export))
    print("🤖 Bot iniciado!")
    app.run_polling()

if __name__ == '__main__':
    main()