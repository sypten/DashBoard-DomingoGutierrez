#datos
import requests
import pandas as pd

#para manipular fechas
import arrow

#gráficos
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def hacerGrafico(fechAnalisis,seleccion,intervalo):

    fechaini=arrow.get(fechAnalisis).timestamp()

    #preparamos la dirección para que se pueda usar con cualquier seleccion
    url = f"https://ftx.com/api/markets/{seleccion}/candles"

    #generamos los argumentos que vamos a usar
    argumentos= {"resolution":intervalo,
        "start_time":fechaini}

    #hacemos la consulta
    respuesta = requests.get(url, params=argumentos)
    #Nos quedamos con la parte result del json que obtenemos de respuesta
    respuesta = respuesta.json()['result']

    #Generamos nuestro df
    monedas = pd.DataFrame(respuesta)

    #convertimos a formato datetime la fecha que nos brinda la consulta
    monedas.startTime = pd.to_datetime(monedas.startTime)

    #Generamos las medias móviles a 99, 25 y 7
    monedas["MA99"]=monedas.close.rolling(window=99).mean()
    monedas["MA25"]=monedas.close.rolling(window=25).mean()
    monedas["MA7"]=monedas.close.rolling(window=7).mean()

    #configuramos nuestro diccionario de colores
    colores = {
        'velasdown': '#EB6D88',
        'velasup': '#23A4F2',
        'fondograf': '#252138',
        'fondotodo':'#2A263D',
        'fondodiv':'3C3956'
    }


    #Creamos un grafico de velas con los datos recolectados
    figura = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.1, 
                            subplot_titles=(f"Evolución de {seleccion} en dólares", 
                                            'Volumen de transacciones'),
                            row_width=[0.2, 0.7],
                        )

    #creamos las Velas
    figura.add_trace(go.Candlestick(x=monedas.startTime,
                                    open=monedas.open,
                                    high=monedas.high,
                                    low=monedas.low,
                                    close=monedas.close,
                                    showlegend=False,
                                    increasing_line_color= colores['velasup'], 
                                    decreasing_line_color= colores['velasdown']
                                    ), row=1, col=1)

    def añadirMA(seriedf,color):
        figura.add_trace(go.Scatter(x=monedas.startTime,
                                    y=seriedf,
                                    line=dict(color=color), #se pueden añadir más detalles a la linea
                                    name=seriedf.name
                                    ), row=1, col=1
                        )

    añadirMA(monedas["MA99"],"#9A94B8")
    añadirMA(monedas["MA25"],"#F1CB81")
    añadirMA(monedas["MA7"],"#ED6F85")


    #creamos un color para el volumen de las velas
    monedas['color']=[colores['velasup'] if (x<y) else colores['velasdown'] for x,y in zip(monedas['open'],monedas['close'])]

    #Creamos los Volumenes
    figura.add_trace(go.Bar(x=monedas.startTime, 
                    y=monedas.volume, 
                    marker_color=monedas['color'],
                    showlegend=False), row=2, col=1)

    #sacamos la barra de navegación que se encuentra debajo
    figura.update_layout(xaxis_rangeslider_visible = False)
                        #paper_bgcolor=colors['fondotodo'], #cambia el color del cuadro contenedor
                        #plot_bgcolor=colors['fondograf'] #cambia el color de lo mas peque
    
    return figura