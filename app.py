from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import io
import base64
import datetime

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Lista pré-definida de moedas suportadas
SUPPORTED_CURRENCIES = [
    'USD', 'EUR', 'BRL', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'INR'
]

# Função para obter a lista de moedas (usando uma lista fixa)
def get_currency_list():
    return SUPPORTED_CURRENCIES

# Função para atualizar a taxa de câmbio e retornar os dados
def update_exchange_rate(base_currency, target_currency):
    url = f"https://economia.awesomeapi.com.br/json/last/{base_currency}-{target_currency}"
    response = requests.get(url)
    data = response.json()
    return data

# Função para obter histórico de taxas de câmbio
def get_exchange_rate_history(base_currency, target_currency):
    url = f"https://economia.awesomeapi.com.br/json/daily/{base_currency}-{target_currency}/30"
    response = requests.get(url)
    data = response.json()
    return data

# Função para plotar o histórico da taxa de câmbio
def plot_exchange_rate_history(history_data):
    dates = []
    rates = []
    for item in history_data:
        try:
            timestamp = int(item['timestamp'])
            date = datetime.datetime.fromtimestamp(timestamp)
            rate = float(item['bid'])
            dates.append(date)
            rates.append(rate)
        except (ValueError, KeyError) as e:
            print(f"Erro ao processar dados de histórico: {e}")
            continue
    
    if dates and rates:
        fig, ax = plt.subplots(figsize=(20, 6))
        ax.plot(dates, rates, marker='o')
        ax.set_title('Histórico da Taxa de Câmbio')
        ax.set_xlabel('Data')
        ax.set_ylabel('Taxa de Câmbio')
        
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        return plot_url
    return None

@app.route('/')
def index():
    return render_template('index.html', currencies=get_currency_list())

@app.route('/convert', methods=['POST'])
def convert():
    base_currency = request.form['base_currency']
    target_currency = request.form['target_currency']
    amount = request.form['amount']

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Por favor, insira um valor numérico válido.'})

    if base_currency and target_currency:
        data = update_exchange_rate(base_currency, target_currency)
        if data and f"{base_currency}{target_currency}" in data:
            rate = data[f"{base_currency}{target_currency}"]['bid']
            converted_amount = amount * float(rate)
            
            # Obter e plotar o histórico da taxa de câmbio
            history_data = get_exchange_rate_history(base_currency, target_currency)
            plot_url = plot_exchange_rate_history(history_data)
            
            return jsonify({'result': f"{converted_amount:.2f} {target_currency}", 'chart': plot_url})
        else:
            return jsonify({'error': 'Dados não encontrados.'})
    else:
        return jsonify({'error': 'Por favor, selecione as moedas e insira o valor.'})

if __name__ == '__main__':
    app.run(debug=True)
