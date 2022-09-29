#datos
import requests
import pandas as pd

def consultarMercados():
    respuesta = requests.get("https://ftx.com/api/markets")
    respuesta = respuesta.json()["result"] #respuesta al estilo una lista de diccionarios
    mercado=pd.DataFrame(respuesta)
    #Nos quedamos con el mercadoa a contado y el cambio con theter a cambio estable
    return mercado.loc[(mercado["type"]=="spot") & mercado.name.str.contains('USDT')]