import tkinter as tk
from flask import Flask, render_template
import plotly.express as px
import yfinance as yf
import requests
import webbrowser

# Crear la aplicación Flask
app = Flask(__name__)

# Función para obtener datos de la acción de Yahoo Finance
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="30d")  # Obtiene los últimos 5 días de datos
        if data.empty:
            print(f"No hay datos disponibles para {symbol}")
            return None
        else:
            return data
    except Exception as e:
        print(f"Error al obtener datos de {symbol}: {e}")
        return None

# Función para obtener la cotización del dólar (tipos de cambio en Argentina)
def get_exchange_rate():
    url = 'https://api.bluelytics.com.ar/v2/latest'  # API de cambio de divisa en Argentina (dólar blue, oficial, etc.)
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        return {
            "Compra Dólar Blue": data['blue']['value_buy'] if 'blue' in data else 'N/A',
            "Venta Dólar Blue": data['blue']['value_sell'] if 'blue' in data else 'N/A',
            "Compra Dólar Oficial": data['oficial']['value_buy'] if 'oficial' in data else 'N/A',
            "Venta Dólar Oficial": data['oficial']['value_sell'] if 'oficial' in data else 'N/A',
            "Compra Euro Blue": data['blue_euro']['value_buy'] if 'blue_euro' in data else 'N/A',
            "Venta Euro Blue": data['blue_euro']['value_sell'] if 'blue_euro' in data else 'N/A',
            "Compra Euro Oficial": data['oficial_euro']['value_buy'] if 'oficial_euro' in data else 'N/A',
            "Venta Euro Oficial": data['oficial_euro']['value_sell'] if 'oficial_euro' in data else 'N/A',
        }
    else:
        print(f"Error al obtener los tipos de cambio: {response.status_code}")
        return {}

# Función para renderizar la página HTML
@app.route('/')
def home():
    stocks = ['AAPL', 'NVDA', 'TSLA', 'GOOGL', 'AMZN', 'SPY', 'GLD', 'BTC-USD', 'ETH-USD', 'HBAR-USD']
    figures = {}

    # Obtener los datos de las acciones
    for stock in stocks:
        stock_data = get_stock_data(stock)
        if stock_data is not None and not stock_data.empty:  # Verificar si el DataFrame no está vacío
            dates = stock_data.index.strftime('%Y-%m-%d').tolist()  # Últimos 5 días
            prices = stock_data['Close'].tolist()
            
            # Crear el gráfico con Plotly
            fig = px.line(x=dates, y=prices, labels={'x': 'Fecha', 'y': 'Precio'}, title=f'Precio de la acción {stock}')
            fig.update_layout(width=500, height=350)  # Ajustar el tamaño del gráfico
            
            # Guardamos el gráfico como una imagen
            fig.write_image(f"static/images/{stock}.png")
            figures[stock] = f"static/images/{stock}.png"

    # Obtener las cotizaciones del dólar
    exchange_rate = get_exchange_rate()

    # Renderizar la página con los datos dinámicos
    return render_template('index.html', figures=figures, exchange_rate=exchange_rate)

# Función para ejecutar Dash
def run_dash():
    app.run(debug=True, host="0.0.0.0", port=8080, use_reloader=False)  # Ejecuta Dash sin el reloader

# Crear la ventana principal de Tkinter
root = tk.Tk()
root.title("Mi Panel Financiero")
root.geometry("1000x800")  # Tamaño de la ventana

# Iniciar Dash en segundo plano (abrir en navegador)
webbrowser.open('http://127.0.0.1:8080/')  # Abre automáticamente el navegador

# Iniciar el servidor Dash en el hilo principal
run_dash()

# Iniciar la ventana Tkinter
root.mainloop()

