import tkinter as tk
from dash import Dash, dcc, html
import plotly.express as px
import yfinance as yf
import requests
import webbrowser

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
        
        # Comprobamos si las claves existen y extraemos los datos correctamente
        return {
            "Compra Dólar Blue": data['blue']['value_buy'] if 'blue' in data else 'N/A',
            "Venta Dólar Blue": data['blue']['value_sell'] if 'blue' in data else 'N/A',
            "Compra Dólar Oficial": data['oficial']['value_buy'] if 'oficial' in data else 'N/A',
            "Venta Dólar Oficial": data['oficial']['value_sell'] if 'oficial' in data else 'N/A',
            "Compra Euro Blue": data['oficial']['value_buy'] if 'blue_euro' in data else 'N/A',
            "Venta Euro Blue": data['oficial']['value_sell'] if 'blue_euro' in data else 'N/A',
            "Compra Euro Oficial": data['oficial']['value_buy'] if 'oficial_euro' in data else 'N/A',
            "Venta Euro Oficial": data['oficial']['value_sell'] if 'oficial_euro' in data else 'N/A',
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
    if stock_data is not None and not stock_data.empty:  # Verificar si el DataFrame no está vacío
        dates = stock_data.index.strftime('%Y-%m-%d').tolist()  # Últimos 5 días
        prices = stock_data['Close'].tolist()
        if prices:
            fig = px.line(x=dates, y=prices, labels={'x': 'Fecha', 'y': 'Precio'}, title=f'Precio de la acción {stock}')
            fig.update_layout(width=500, height=350)  # Ajustar el tamaño del gráfico
            figures[stock] = fig
        else:
            print(f"No se encontraron precios válidos para {stock}.")
    else:
        print(f"No se pudieron obtener datos para la acción {stock}, se omitirá el gráfico.")

# Crear la aplicación Dash
app = Dash(__name__)

# Layout de la aplicación Dash
app.layout = html.Div(children=[
    html.H1('Panel de Datos Financieros', style={'textAlign': 'center', 'color': 'white', 'padding': '20px'}),
    
    # Contenedor para los gráficos, se usan dos por fila
    html.Div([
        html.Div([dcc.Graph(id=f'grafico-{stock}', figure=figures[stock], style={'height': '300px', 'width': '48%'}) for stock in stocks[:5]]),  # Fila 1
        html.Div([dcc.Graph(id=f'grafico-{stock}', figure=figures[stock], style={'height': '300px', 'width': '48%'}) for stock in stocks[5:10]]),  # Fila 2
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around', 'padding': '10px'}),

    # Cuadro con cotizaciones del dólar en colores llamativos
    html.Div([
        html.H3('Cotización del Dólar en Argentina', style={'color': 'white', 'textAlign': 'center'}),
        html.Div(id='info-dolar', children=[
            html.Div(f"Compra Dólar Blue: {get_exchange_rate().get('Compra Dólar Blue', 'N/A')} ARS", style={'backgroundColor': '#18ad5b', 'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'margin': '5px'}),
            html.Div(f"Venta Dólar Blue: {get_exchange_rate().get('Venta Dólar Blue', 'N/A')} ARS", style={'backgroundColor': '#47cd83', 'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'margin': '5px'}),
            html.Div(f"Compra Dólar Oficial: {get_exchange_rate().get('Compra Dólar Oficial', 'N/A')} ARS", style={'backgroundColor': '#18ad5b', 'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'margin': '5px'}),
            html.Div(f"Venta Dólar Oficial: {get_exchange_rate().get('Venta Dólar Oficial', 'N/A')} ARS", style={'backgroundColor': '#47cd83', 'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'margin': '5px'}),
            html.Div(f"Compra Euro Blue: {get_exchange_rate().get('Compra Euro Blue', 'N/A')} ARS", style={'backgroundColor': '#0e7be4', 'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'margin': '5px'}),
            html.Div(f"Venta Euro Blue: {get_exchange_rate().get('Venta Euro Blue', 'N/A')} ARS", style={'backgroundColor': '#48a4fd', 'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'margin': '5px'}),
            html.Div(f"Compra Euro Oficial: {get_exchange_rate().get('Compra Euro Oficial', 'N/A')} ARS", style={'backgroundColor': '#0e7be4', 'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'margin': '5px'}),
            html.Div(f"Venta Euro Oficial: {get_exchange_rate().get('Venta Euro Oficial', 'N/A')} ARS", style={'backgroundColor': '#48a4fd', 'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'margin': '5px'}),
        ], style={'padding': '20px', 'backgroundColor': '#333333', 'borderRadius': '10px', 'marginTop': '20px'})
    ], style={'padding': '20px'}),
])

# Función para ejecutar Dash
def run_dash():
    app.run(debug=True, use_reloader=False)  # Ejecuta Dash sin el reloader

# Crear la ventana principal de Tkinter
root = tk.Tk()
root.title("Mi Panel Financiero")
root.geometry("1000x800")  # Tamaño de la ventana

# Iniciar Dash en segundo plano (abrir en navegador)
webbrowser.open('http://127.0.0.1:8050/')  # Abre automáticamente el navegador

# Iniciar el servidor Dash en el hilo principal
run_dash()

# Iniciar la ventana Tkinter
root.mainloop()
