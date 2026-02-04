'''COMANDO PARA RODAR: python3 -m streamlit run fut.py'''

import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Estatisticas La Liga",
    page_icon="📊",
    layout="wide"
)

df_artilheiros = pd.read_csv('dados_artilheiros.csv')
df_partidas = pd.read_csv('dados_partidas.csv')

st.sidebar.header("🔍 Filtros")

times_disp = df_artilheiros['Time'].unique()
times_selec = st.sidebar.multiselect("Time", times_disp, default=times_disp)

jogadores_disp = df_artilheiros["Artilheiro"].unique()
jogadores_selec = st.sidebar.multiselect("Jogadores", jogadores_disp, default=jogadores_disp)

def pontos_casa(row):
    if row["gols_casa"] > row["gols_fora"]:
        return 3
    elif row["gols_casa"] == row["gols_fora"]:
        return 1
    else:
        return 0

def pontos_fora(row):
    if row["gols_fora"] > row["gols_casa"]:
        return 3
    elif row["gols_fora"] == row["gols_casa"]:
        return 1
    else:
        return 0


df_partidas["pontos_casa"] = df_partidas.apply(pontos_casa, axis=1)
df_partidas["pontos_fora"] = df_partidas.apply(pontos_fora, axis=1)

casa = df_partidas[["time_casa", "pontos_casa"]].rename(columns={"time_casa": "time", "pontos_casa": "pontos"})

fora = df_partidas[["time_fora", "pontos_fora"]].rename(columns={"time_fora": "time", "pontos_fora": "pontos"})

tabela = (
    pd.concat([casa, fora]).groupby("time", as_index=False).sum().sort_values("pontos", ascending=False)
)

print(tabela)

dfa_filtrado = df_artilheiros[
    (df_artilheiros['Artilheiro'].isin(jogadores_selec)) &
    (df_artilheiros['Time'].isin(times_selec)) &
    (df_artilheiros['Partidas'].notna()) &
    (df_artilheiros['Gols'].notna()) &
    (df_artilheiros['Assistencias'].notna())
]

dfp_filtrado = df_partidas[
    (df_partidas['time_casa'].isin(times_selec)) &
    (df_partidas['time_fora'].isin(times_selec)) &
    (df_partidas['gols_casa'].notna()) &
    (df_partidas['gols_fora'].notna())
]
st.title("🎲 Dashboard de Estatisticas da La Liga")
st.markdown("Explore os dados da liga. Utilize os filtros à esquerda para refinar sua análise.")


if not dfa_filtrado.empty:
    dfp_filtrado = df_partidas.copy()

    dfp_filtrado['gols_casa_validos'] = dfp_filtrado['gols_casa'].where(
    dfp_filtrado['time_casa'].isin(times_selec), 0
    )

    dfp_filtrado['gols_fora_validos'] = dfp_filtrado['gols_fora'].where(
    dfp_filtrado['time_fora'].isin(times_selec), 0
    )

    total_gols = dfp_filtrado['gols_casa_validos'].sum() + dfp_filtrado['gols_fora_validos'].sum()

    maior_goleador = dfa_filtrado.loc[dfa_filtrado['Gols'].idxmax(), 'Artilheiro']
    gols_art = dfa_filtrado.loc[dfa_filtrado['Gols'].idxmax(), 'Gols']
else:
    total_gols, maior_goleador, gols_art = 0, 0, 0

col1, col2, col3 = st.columns(3)
col1.metric("Total de gols", f"{total_gols}")
col2.metric("Maior goleador", f"{maior_goleador}")
col3.metric("Quantidade de gols", f"{gols_art}")

st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not dfa_filtrado.empty:
        graficos_artilheiros = px.bar(
            dfa_filtrado,
            x='Artilheiro',
            y='Gols',
            title="Artlheria",
            labels={'Artilheiro': 'Nome do jogador', 'Gols': 'Gols'}
        )
        graficos_artilheiros.update_layout(title_x=0.1)
        st.plotly_chart(graficos_artilheiros, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    st.dataframe(tabela['time'])