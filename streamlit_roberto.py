import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from PIL import Image


logo_todos = Image.open('/home/pedro/Dropbox/pedro_programas/logos_juntas.png')  # Substitua pelo caminho da sua imagem
logo_embrapa = Image.open('/home/pedro/Dropbox/pedro_programas/logo_embrapa.png')
logo_unb = Image.open('/home/pedro/Dropbox/pedro_programas/logo_unb.png')
logo_capes = Image.open("/home/pedro/Dropbox/pedro_programas/capes_fapdf.png")

  # Linha horizontal acima do rodapé
col1, col2, col3, col4  = st.columns(4)

with col1:
    st.image(logo_embrapa, width=200)

with col2:
    st.write("")

with col3:
    st.write("")
    
with col4:
    st.image(logo_unb, width= 160)

st.markdown("<hr>", unsafe_allow_html=True)

# Layout principal
st.title('Data Processing')
st.write('Importe aqui os dados da sua tabela')


df = st.file_uploader('Upload a CSV/ txt/ excel  file')
if df is not None:
    tabela= pd.read_csv(df, sep = "\t", encoding= 'UTF-16', skiprows= 2, skipfooter= 3, dtype='float', decimal=',')
    tabela.drop(['Temperature(¡C)'], axis= 'columns', inplace = True)
    tabela_fitted = tabela.fillna(0)   

    #st.write(tabela_fitted)
    #lista das células cheias:
    tabela_valores = tabela.dropna(axis=1, how='all')
    #st.write(tabela_valores)
    lista_celulas_cheias = list(tabela_valores)
    
#fazendo placa pra ver quauis as células estão vazias:

    placa_df = pd.DataFrame(index = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
                        columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
    index = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
#preenchendo as colunas com A1 A2 A3...
    for z in index:
        for e in columns:
            b = z+e
            placa_df.loc[z, e] = b

    def color_cells(val):
        if  val in lista_celulas_cheias:
            color = 'white'
            return 'background-color: gray'; 'color: %s' % color
        else:
            pass 
        
    styled_df = placa_df.style.applymap(color_cells)

    st.write('Segue a baixo o resultado do teste as células verdes são os resultados negativos:')
    st.dataframe(styled_df)

    controle_p = st.multiselect('Select the cels that are positive controls', options =[i for i in lista_celulas_cheias if i != 'Wavelength'], max_selections= 2)
    
    if controle_p == None:
        st.write("waiting you to chose your control...")
    elif len(controle_p) == 2:
        controle_n = st.multiselect('Select the cels that are negative controls', options =[i for i in lista_celulas_cheias if i not in [*controle_p, 'Wavelength']], max_selections= 2)
        #calculando o resultado:
        
        if controle_n == None:
            st.write("waiting you to chose yor negative control")
        elif len(controle_n) == 2:
            tabela['media_controle_p'] = (tabela[controle_p[0]] + tabela[controle_p[1]])/2
            tabela['media_controle_n'] = (tabela[controle_n[0]] + tabela[controle_n[1]])/2

            tabela['Ratio_controle'] = tabela['media_controle_p'] - tabela['media_controle_n']  

            maior_pico_ratio_controle = tabela.loc[(tabela['Wavelength'].values > 630) & (tabela['Wavelength'].values < 680)]['Ratio_controle'].max()




            resultado = []
            for i in tabela.columns:
                if i not in [*controle_n, *controle_p, 'Wavelength']:
                    tabela['Ratio_tratamento'] = tabela[i] - tabela['media_controle_n']
                    maior_pico_ratio_tratamento = tabela.loc[(tabela['Wavelength'].values > 630) & (tabela['Wavelength'].values < 680)]['Ratio_tratamento'].max()
                    if maior_pico_ratio_tratamento > maior_pico_ratio_controle: 
                        resultado.append((i , 'Positivo'))

                    else:
                        resultado.append((i, 'Negativo'))
                        
    #fazendo o dicionario para fazer o replace das células do data frame com os resultados:
            pos = []
            res = []
            for l in resultado:
                pos.append(l[0])
                res.append(l[1])

            dicionario = dict(zip(pos, res))
        
    #replace das células ao inves de aparecer as cordenadas aparecer os resultados entre negativo e positivo
            for z in index:
                for e in columns:
                    b = z+e
                    if b in pos:
                        placa_df.loc[z, e] = dicionario[b]
                    else:
                        placa_df.loc[z, e] = 'Controle'
                

            def color_cells(val):
                if  val == 'Positivo':
                    color = 'white'
                    return 'background-color: red'; 'color: %s' % color
                elif val == 'Controle':
                    color = 'white'
                    return 'background-color: blue'; 'color: %s' % color
                else:
                    color = 'white'
                    return 'background-color: green'; 'color: %s' % color
                
            #mostrando o dataframe:
            
            styled_df = placa_df.style.applymap(color_cells)

            st.write('Segue a baixo o resultado do teste as células verdes são os resultados negativos:')
            st.dataframe(styled_df)
            #daqui pra frente é aggrid
            colors = JsCode("""
                function(params){
                    if (params.value == "Positivo ") {
                        return {
                        'color': 'black',
                        'backgroundColor': 'green'
                        }
                    }
                    if (params.value == "Negativo") {
                        return {
                        'color': 'black',
                        'backgroundColor': 'red'
                        }
                    }
                    else{
                        return{
                        'color' : 'white',
                        'backgroundColor': 'blue'
                        }
                    }
                };
            
            """)
            gb = GridOptionsBuilder.from_dataframe(placa_df)
            gb.configure_default_column(editable=True)
            for i in list(placa_df):
                gb.configure_columns(i , cellStyle= colors)
            grid_options = gb.build()
            #AgGrid(placa_df, gridOptions= grid_options, allow_unsafe_jscode= True)

            coluna_gráfico = st.multiselect('select the cells u wanna plot', options =[i for i in tabela.columns if i not in [*controle_p, 'Wavelength']], max_selections= 2)
# até aqui é ag grid 
# definindo a figura no matplot lib
            if coluna_gráfico == None:
                st.write("waiting for you to chose a ")
            elif len(coluna_gráfico) == 2:

                fig, ax = plt.subplots(figsize = (25,15))
    #adicionanfo as linhas na figura em branco (ax)
    #definir eixo x e y; definir qual é a tabela no data; label = legenda; linewidth = grossura da linha; ax = ax quer dizer que o eixo da coluna esta no eixo da figura 
                sns.lineplot(x = 'Wavelength',
                            y = 'media_controle_p',
                            data = tabela,
                            label = 'Controle Media Positivo',
                            linewidth = 5.5,
                            ax = ax)
                sns.lineplot(x = 'Wavelength',
                            y = 'media_controle_n',
                            label = 'Controle Media Negativo',
                            linewidth = 5.5,
                            data = tabela,
                            ax = ax)
                sns.lineplot(x = 'Wavelength',
                            y = coluna_gráfico[0],
                            label = f'{coluna_gráfico[0]} Media',
                            linewidth = 5.5,
                            data = tabela,
                            ax = ax)
                sns.lineplot(x = 'Wavelength',
                            y = coluna_gráfico[1],
                            label = f'{coluna_gráfico[1]} Media',
                            linewidth = 5.5,
                            data = tabela,
                            ax = ax)

                ax.set_ylim(-10, 600)

                ax.set_xlabel("Wavelength",fontsize=30)
                ax.set_ylabel("",fontsize=20)

                ax.legend(fontsize = 25)

                plt.tick_params(labelsize=25)

                
                st.pyplot(fig)
            else:
                st.write("escolha as celulas a serem plotadas")
        else:
            st.write('escolha um controle positivo')
    else:
        st.write('escolha o controle positivo')
# Adicionando as imagens no rodapé
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.markdown("<hr>", unsafe_allow_html=True)  # Linha horizontal acima do rodapé
col1, col2, col3 = st.columns(3)

with col1:
    st.image(logo_capes, width=210)

with col2:
    st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
    .custom-font {
        font-family: 'Roboto', sans-serif;
        font-size: 10px;
        color: white;
    }
    </style>
    <p class="custom-font" align = justify >Embrapa Recursos Genéticos e Biotecnologia \n Laboratório de Bioinformática \n Parque Estação Biológica, PqEB, Av. W5 Norte (final) \n Caixa Postal 02372 – Brasília, DF – CEP 70770-917 \n Fone: +55(61)3448-4741</p>
    """,
    unsafe_allow_html=True
)

with col3:
    st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
    .custom-font {
        font-family: 'Roboto', sans-serif;
        font-size: 10px;
        color: white;
    }
    </style>
    <p class="custom-font" align = justify >Universidade de Brasília \n Departamento de Genética e Morfologia/IB \n Campus Darcy Ribeiro \n 70910-900, Brasília, DF, Brazil \n Fone +55(61)3107-3078</p>
    """,
    unsafe_allow_html=True
)



    
    

     
