#datos
from mercados import consultarMercados
#import pandas as pd

#para manipular fechas
from datetime import datetime, timedelta

#gráficos
from grafico import hacerGrafico
#import plotly.graph_objects as go
#from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State, ctx

app = Dash(__name__)

# Para setear el color de los gráficos a uno solo con el del fondo general
"""dcc.Graph(
id='example-graph-2',
figure={
    'layout': {
        'plot_bgcolor': colors['background'],
        'paper_bgcolor': colors['background'],
        'font': {
            'color': colors['text']
        }
    }"""

mercados=consultarMercados()
#contenedor principal
app.layout = html.Div([

    #Parte izquierda
    html.Div([
        html.Div([
            html.H1(id='nombreMoneda'),
            dcc.Dropdown(mercados['name'], 'BTC/USDT', id='monedaElegida',
            clearable=False)
        ]),
        
        
        # Paridad, conversión inversa
        html.Br(),
        html.Div([
            html.Div(
                dcc.Input(
                    placeholder='1',
                    type='text',
                    value='1',
                    id='cantidad',
                    #Estilo del input
                    style={'max-width':'20px',
                            'margin':'50% 0'}

                #Estilo del div contenedor de la entrada de Paridad
                ),style={#'max-width':'10%', 
                        #'flex':'1 10%',
                        'padding': '5px', 
                        'margin':'10px',
                        'align-content': 'center',
                        "float": "left"}
            ),

            #Resultado de La conversión de Paridad
            html.Div(id='paridad', 
                style={'align-content': 'center',
                        #'max-width':'70%', 
                        'flex':'1 80%',
                        "padding": '5px', 
                        'margin':'10px 0', 
                        "float": "right"})
        
        #Estilo del bloque de conversión de Paridad
        ], style={'display': 'flex', 'flex-direction': 'colum'}),
        #style={'diplay':'block', 'margin':'20px 0px'}),

        #calculadora
        html.Br(),
        html.Div([
            html.Div([
                html.Label('Ingrese monto a convertir'),
                dcc.Input(id='input-box', 
                            type='text',
                            placeholder='1',
                            value='1')],
            style={'flex':1}),#,'flex-direction':'row'}),

            html.Br(),
            html.Div([
                html.Label('Seleccione moneda de Destino'),
                dcc.Dropdown(mercados['name'], 'BTC/USDT', id='monedaDestino'),
                html.Br(),
                html.Button('Convertir', id='button-example-1',

                    style={'min-width':'100%'})
            
            ],style={'flex':1,'flex-direction':'row'}),

            html.Br(),
            html.Div(id='output-container-button',
             children='Enter a value and press submit')

        ])

        #El estilo corresponde al div contenedor de la parte izquierda
        ],className='divIzq'),


    #Parte derecha
    html.Div([#parte derecha
        html.Div([ #parte arriba

            #primera columna
            html.Div([
                #precio de la moneda seleccionada              
                html.Label('Precio en dólares'),
                html.H1(id='precioMoneda', className='titulos')
            ], className='caja'),

            #segunda columna
            html.Div([
                html.Label('Volumen en dólares'),
                html.H1(id='volumenMoneda', className='titulos')
            ], className='caja')
            
            #estilo parte arriba derecha
            ], className='divDer'),
        
        #Caja contenedora del gráfico
        html.Div(
            dcc.Graph(id='figura')
            )

        #estilo parte derecha  
        ], style={'flex':'1 75%'})



    #estilo todo el layout
    ], style={'display': 'flex', 'flex-direction': 'row', 'margin': 10}
)





#Grafico según selección
@app.callback(
    Output('figura','figure'),
    Input('monedaElegida','value')
)
def grafico_moneda(moneda):
    #establecemos una fecha a 4 meses
    fechanalisis=datetime.now()-timedelta(120)
    grafico=hacerGrafico(fechanalisis,moneda,86400)
    return grafico


# Precio Actual currency
@app.callback(
    Output(component_id='precioMoneda', component_property='children'),
    Input(component_id='monedaElegida', component_property='value')
)
def actualizar_h1_moneda(input_value):
    #devuelve el valor En USD de la moneda elegida
    precio=float(mercados[mercados.name==input_value]['price'].values)
    return f'{precio:,.2f} $'


# Nombre de la moneda elegida
@app.callback(
    Output(component_id='nombreMoneda', component_property='children'),
    Input(component_id='monedaElegida', component_property='value')
)
def actualizar_titulo_moneda(input_value):
    #devuelve el valor En USD de la moneda elegida
    return input_value


# Volumen Moneda Seleccionada
@app.callback(
    Output(component_id='volumenMoneda', component_property='children'),
    Input(component_id='monedaElegida', component_property='value')
)
def actualizar_h1_volumen(input_value):
    #devuelve el valor En USDT de la moneda elegida
    volumen=float(mercados[mercados.name==input_value]['volumeUsd24h'].values)
    return f'{volumen:,.2f} $'


# Paridad Moneda Seleccionada
@app.callback(
    Output(component_id='paridad', component_property='children'),
    Input(component_id='monedaElegida', component_property='value'),
    Input('cantidad', 'value')
)
def paridad_moneda(moneda, cantidad = 1):
    #devuelve el valor En USDT de la moneda elegida
    cantidad=float(cantidad)
    precio=float(mercados[mercados.name==moneda]['price'].values)
    salida=cantidad/precio
    if cantidad==1:
        return f'dólar son {salida:.10f} {moneda[:-5]}'
    elif cantidad>1:
        return f'dólares son {salida:.10f} {moneda[:-5]}'
    else:
        return 'no ingresó una cantidad válida'


# Calculadora
@app.callback(
    Output('output-container-button', 'children'),
    Input('button-example-1', 'n_clicks'),
    State('monedaElegida', 'value'),
    State('monedaDestino', 'value'),
    State('input-box', 'value')
)
def actualizar_boton(n_clicks, desde, hasta, multiplicador=1):

    if 'button-example-1'== ctx.triggered_id:
    #conseguimos el precio de la moneda ingresada
        multiplicador=float(multiplicador)
        entrada=float(mercados[mercados.name==desde]['price'].values)
        destino=float(mercados[mercados.name==hasta]['price'].values)
        salida=entrada/destino
        return f'{multiplicador} {desde} valen {multiplicador*salida:.10f} {hasta}'


if __name__ == '__main__':
    app.run_server(debug=True) 
    #dash automaticamente refrescará lo visualizado 
    #al hacer cambios en el código