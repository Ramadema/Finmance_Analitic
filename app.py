import tkinter as tk
from dash import Dash, dcc, html
import plotly.express as px
import yfinance as yf
import requests
import threading
import webbrowser

# Función para obtener datos de la acción de Yahoo Finance
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="5d")  # Obtiene los últimos 5 días de datos
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
        
        # Comprobamos si la clave 'mep' existe antes de acceder
        return {
            "Dólar Blue": data['blue']['value_sell'],
            "Dólar Oficial": data['oficial']['value_sell'],
            "Dólar MEP/Bolsa": data.get('mep', {}).get('value_sell', 'N/A'),
            "Contado con Liqui": data.get('cc_liqui', {}).get('value_sell', 'N/A'),
            "Dólar Cripto": data.get('crypto', {}).get('value_sell', 'N/A')
        }
    else:
        print(f"Error al obtener los tipos de cambio: {response.status_code}")
        return {}

# Lista de acciones que quieres graficar
stocks = ['AAPL', 'NVDA', 'TSLA', 'GOOGL', 'AMZN', 'SPY', 'GLD', 'BTC-USD', 'ETH-USD', 'HBAR-USD']

# Crear los gráficos de las acciones solicitadas
figures = {}
for stock in stocks:
    stock_data = get_stock_data(stock)
    if stock_data is not None and not stock_data.empty:
        dates = stock_data.index.strftime('%Y-%m-%d').tolist()  # Últimos 5 días
        prices = stock_data['Close'].tolist()
        fig = px.line(x=dates, y=prices, labels={'x': 'Fecha', 'y': 'Precio'}, title=f'Precio de la acción {stock}')
        figures[stock] = fig
    else:
        print(f"No se pudieron obtener datos para la acción {stock}, se omitirá el gráfico.")

# Crear la aplicación Dash
app = Dash(__name__)

# Layout de la aplicación Dash
app.layout = html.Div(children=[
    html.H1('Panel de Datos Financieros'),
    
    # Mostrar gráficos de las acciones
    html.Div([
        dcc.Graph(id=f'grafico-{stock}', figure=figures[stock]) for stock in stocks if stock in figures
    ]),
    
    html.H3('Cotizaciones'),
   # Cuadro con cotizaciones del dólar en colores llamativos
    html.Div([
        html.H3('Cotización del Dólar en Argentina', style={'color': 'white', 'textAlign': 'center'}),
        html.Div(id='info-dolar', children=[
            html.Div(f"Dólar Blue: {get_exchange_rate().get('Dólar Blue', 'N/A')} ARS", style={'backgroundColor': '#ff6347', 'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'margin': '5px'}),
            html.Div(f"Dólar Oficial: {get_exchange_rate().get('Dólar Oficial', 'N/A')} ARS", style={'backgroundColor': '#3cb371', 'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'margin': '5px'}),
            html.Div(f"Dólar MEP/Bolsa: {get_exchange_rate().get('Dólar MEP/Bolsa', 'N/A')} ARS", style={'backgroundColor': '#1e90ff', 'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'margin': '5px'}),
            html.Div(f"Contado con Liqui: {get_exchange_rate().get('Contado con Liqui', 'N/A')} ARS", style={'backgroundColor': '#f0e68c', 'padding': '10px', 'borderRadius': '5px', 'color': 'black', 'margin': '5px'}),
            html.Div(f"Dólar Cripto: {get_exchange_rate().get('Dólar Cripto', 'N/A')} ARS", style={'backgroundColor': '#dda0dd', 'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'margin': '5px'})
        ], style={'padding': '20px', 'backgroundColor': '#333333', 'borderRadius': '10px', 'marginTop': '20px'})
    ], style={'padding': '20px'}),
])

# Función para ejecutar Dash
def run_dash():
    app.run(debug=True, use_reloader=False)  # Ejecuta Dash sin el reloader

# Crear la ventana principal de Tkinter
root = tk.Tk()
root.title("Mi Panel Financiero")
root.geometry("800x600")  # Tamaño de la ventana

# Iniciar Dash en segundo plano (abrir en navegador)
webbrowser.open('http://127.0.0.1:8050/')  # Abre automáticamente el navegador

# Iniciar el servidor Dash en el hilo principal
run_dash()

# Iniciar la ventana Tkinter
root.mainloop()
