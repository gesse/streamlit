import streamlit as st 
import pandas as pd
import numpy as np
from pycaret.regression import load_model, predict_model
from pycaret.datasets import get_data

st.header('Deploy do Modelo de Previsão de Preços de Diamante')
st.write('Entre com as caracteristicas do diamante para fazer uma previsão do preço de venda do mesmo')
st.markdown('---')

dados = get_data('diamond')
modelo = load_model('recursos/modelo-previsao-preco-diamante')

#Widgets para fazer os inputs do modelo
#
#Peso em quilates (Carat Weight): O peso do diamante em quilates. Um quilate equivale a 0,2 gramas, aproximadamente o mesmo peso de um clipe de papel
#Corte (Cut): Um dos cinco valores que indicam o corte do diamante na seguinte ordem de desejabilidade (Assinatura-Ideal, Ideal, Muito Bom, Bom, Justo)
#Cor (Color): Um dos seis valores que indicam a cor do diamante na seguinte ordem de conveniência (D, E, F - Incolor, G, H, I - Quase incolor)
#Clareza (Clarity): Um dos sete valores que indicam a clareza do diamante na seguinte ordem de desejabilidade (F - Impecável, IF - Internamente Impecável, VVS1 ou VVS2 - Muito, Muito Ligeiramente Incluído, ou VS1 ou VS2 - Muito Ligeiramente Incluído, SI1 - Ligeiramente Incluído )
#Polimento (Polish): Um dos quatro valores que indicam o polimento do diamante (ID - Ideal, EX - Excelente, VG - Muito Bom, G - Bom)
#Simetria (Symmetry): Um dos quatro valores que indicam a simetria do diamante (ID - Ideal, EX - Excelente, VG - Muito Bom, G - Bom)
#Relatório (Report): Um dos dois valores "AGSL" ou "GIA" indicando qual agência de classificação relatou as qualidades dos diamantes
#Preço (Price): o valor em dólares americanos em que o diamante é avaliado. Coluna de destino

#Data columns (total 8 columns):
# #   Column        Non-Null Count  Dtype  
#---  ------        --------------  -----  
# 0   Carat Weight  6000 non-null   float64
# 1   Cut           6000 non-null   object 
# 2   Color         6000 non-null   object 
# 3   Clarity       6000 non-null   object 
# 4   Polish        6000 non-null   object 
# 5   Symmetry      6000 non-null   object 
# 6   Report        6000 non-null   object 
# 7   Price         6000 non-null   int64  
#dtypes: float64(1), int64(1), object(6)


def trad_cut(x):
    if x == 'Signature-Ideal':
        return 'Excelente (lapidação mais alta e desejável)'
    elif x == 'Ideal':
        return 'Ideal (lapidação alta e desejável)'
    elif x == 'Very Good':
        return 'Muito Boa'
    elif x == 'Good':
        return 'Boa'
    elif x == 'Fair':
        return 'Aceitável'

def trad_color(x):
    if x == 'D':
        return 'Excepcionalmente incolor extra'
    elif x == 'E':
        return 'Excepcionalmente incolor'
    elif x == 'F':
        return 'Perfeitamente incolor'
    elif x == 'G':
        return 'Nitidamente incolor'
    elif x == 'H':
        return 'Incolor'
    elif x == 'I':
        return 'Cor levemente perceptível'

def trad_clarity(x):
	if x == 'F':
		return 'Internamente e externamento puro'
	elif x == 'IF':
		return 'Internamente livre de inclusões'
	elif x == 'VVS1':
		return 'Inclusão pequeniníssima'
	elif x == 'VVS2':
		return 'Inclusões pequeniníssimas'
	elif x == 'VS1':
		return 'Inclusão muito pequena'
	elif x == 'VS2':
		return 'Inclusões muito pequenas'

def trad_polish(x):
	if x == 'ID':
		return 'Ideal (superfície mais suave e perfeita)'
	elif x == 'EX':
		return 'Excelente (superfície muito suave e de alta qualidade)'
	elif x == 'VG':
		return 'Muito boa (superfície bastante suave mas com imperfeições microscópicas)'
	elif x == 'G':
		return 'Boa (superfície  suave mas com imperfeições mais visíveis)'

def trad_symmetry(x):
	if x == 'ID':
		return 'Ideal (todas as facetas perfeitamente alinhadas e encaixadas umas nas outras)'
	elif x == 'EX':
		return 'Excelente (facetas muito bem alinhadas e encaixadas, mas com pequenas imperfeições)'
	elif x == 'VG':
		return 'Muito boa (facetas muito bem alinhadas e encaixadas, mas com pequenas imperfeições mais visíveis)'
	elif x == 'G':
		return 'Boa (imperfeições mais visíveis nas facetas, o que pode afetar a aparência geral do diamante.)'

def trad_report(x):
	return 'American Gem Society Laboratories' if x == 'AGSL' else 'Gemological Institute of America'

weight = st.number_input(label = 'Peso (em Quilates):', 
				min_value = 0.75, 
				max_value = 2.91, 
				step = 0.01)

cut = st.radio('Lapidação (corte):', 
				['Signature-Ideal', 'Ideal', 'Very Good', 'Good', 'Fair'], 
				index=None,
				format_func = trad_cut)

color = st.selectbox(label = 'Cor:', 
						options = ['D', 'E', 'F', 'G', 'H', 'I'],
						format_func = trad_color,
						index=None,
						placeholder='Selecione a cor do diamante ...',
						help='Quanto menos cor um diamante apresenta, maior seu valor de venda')

clarity = st.selectbox(label = 'Grau de Pureza:', 
						options = ['F', 'IF', 'VVS1', 'VVS2', 'VS1', 'VS2'],
						format_func = trad_clarity,
						index=None,
						placeholder='Selecione o grau de pureza ...',
						help='O grau de pureza do diamante se refere à presença (ou não) de inclusões e manchas que possam diminuir seu valor')

polish = st.radio('Tipo do Polimento:', 
					['ID', 'EX', 'VG', 'G'],
					format_func = trad_polish,
					index=None,
					help='Se refere à suavidade e qualidade da superfície do diamante após o processo de corte e lapidação')

symmetry = st.radio('Simetria:', 
					['ID', 'EX', 'VG', 'G'],
					format_func = trad_symmetry,
					index=None,
					help='Se refere à forma como as facetas (as superfícies planas e polidas) do diamante se alinham e se encaixam umas nas outras')

report = st.radio('Avaliação realizada por:', 
					['AGSL', 'GIA'],
					format_func = trad_report,
					index=None,
					help='Organização que avaliou e emitiu um relatório com as características do diamante')

#Criar um DataFrame com os inputs exatamente igual ao dataframe em que foi treinado o modelo
aux = {'Carat Weight': [weight],
		'Cut': [cut],
		'Color': [color],
		'Clarity': [clarity],
		'Polish': [polish],
		'Symmetry': [symmetry],
		'Report': [report]}

prever = pd.DataFrame(aux)

#st.write(prever)

#Usar o modelo salvo para fazer previsao nesse Dataframe

botao = st.button('Calcular preço do Diamante',
					type = 'primary',
					use_container_width = True)


if botao:
	campos_preenchidos = True

	if not cut:
	    st.warning('Por favor, selecione o Tipo de Lapidação antes de calcular o preço.')
	    campos_preenchidos = False

	if not color:
	    st.warning('Por favor, selecione a Cor do Diamante antes de calcular o preço.')
	    campos_preenchidos = False

	if not clarity:
	    st.warning('Por favor, selecione o Grau de Pureza do Diamante antes de calcular o preço.')
	    campos_preenchidos = False

	if not polish:
	    st.warning('Por favor, selecione o Tipo de Polimento do Diamante antes de calcular o preço.')
	    campos_preenchidos = False

	if not symmetry:
	    st.warning('Por favor, selecione a Simetria do Diamante antes de calcular o preço.')
	    campos_preenchidos = False

	if not report:
	    st.warning('Por favor, selecione o Órgão que fez a avaliação do Diamante.')
	    campos_preenchidos = False

	if campos_preenchidos:
		previsao = predict_model(modelo, data = prever)
		valor = round(previsao.loc[0,'prediction_label'], 2)
		st.write(f'### O preço previsto pelo modelo é de: ${valor}')


