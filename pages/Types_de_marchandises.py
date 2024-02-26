import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from st_pages import Page, show_pages, add_page_title
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster




# ce qui se met sur la fenetre du site
st.set_page_config(page_title= "Dashboard", page_icon= "🌍", layout= "wide")
#st.subheader("🔔 Analyse de la concurrence dans le secteur du transport de marchandises")
st.subheader("📊 Étude du marché dans le secteur du transport routier de marchandises en Centre-Val-de-Loire")

# Mettre en table

tab1, tab2,tab3,tab4 = st.tabs(["Types de marchandises","Volume de marchandises", "Taux d'évolution sur 8 ans", "Top 5 régions partenaires"])
with tab1:

    # Titre du graphique

    st.markdown("##")



    # Importer le jeu de données entreprises de transport de marchandises
    df_type_marchandises= pd.read_csv("nouvelle_data/type_marchandises_tranp_Centre_2021.csv")






    # Titre du filtre sur le département de chargement
    st.sidebar.header("Filtrer une région")

    # Filtrer le DataFrame en fonction des régions sélectionnées
    df_filtre = df_type_marchandises[df_type_marchandises["Regions_de_chargement"]=="Regions_de_chargement"]



    Regions_de_chargement= st.sidebar.multiselect(
    "Selectionner le Centre-Val-de-Loire",
    options= ["Centre — Val de Loire"],#options_regions,
    default= ["Centre — Val de Loire"]#options_regions
    #key="departement_key"  # Remplacez "departement_key" par une clé unique
    )


    Regions_de_dechargement =  st.sidebar.multiselect(
    "Selectionner une région de déchargement ",
    options= df_type_marchandises["Regions_de_dechargement"].unique(),
    default= df_type_marchandises["Regions_de_dechargement"].unique(),
    #key="Classe_key"  # Remplacez "departement_key" par une clé unique
    )




    df_select= df_type_marchandises.query( 
    "Regions_de_chargement== @Regions_de_chargement & Regions_de_dechargement == @Regions_de_dechargement"
    )


    def Home():
        with st.expander("Tabulaire"): 
            showData= st.multiselect("Filtrer:", df_select.columns, default=[])
            st.write(df_select[showData])

        st.subheader('Top 10 des marchandises transportées par le Centre-Val-de-Loire en 2021', divider='rainbow')

    def graph():

        df_Centre= df_select[df_select['Regions_de_chargement'] == 'Centre — Val de Loire']

        # 2. Grouper par type de marchandises et calculer la somme des Tkm
        group_par_marchand = df_Centre.groupby("Marchandises")["Tkm(en millions)"].sum().reset_index()

        # 3. Trier les résultats pour obtenir le top 10
        top_10_marchandises = group_par_marchand.sort_values(by="Tkm(en millions)", ascending=False).head(10)

        # 4. Créer le graphique avec Plotly Express
        fig = px.bar(top_10_marchandises, x="Tkm(en millions)", y="Marchandises", orientation= 'h', title="Tonnes-kilomètres (en millions)",
                    labels={"Tkm(en millions)": "Tonnes-kilomètres (en millions)"}, color="Marchandises",
                    text_auto= True)
        fig.update_yaxes(title_text= None)
        fig.update_xaxes(title_text= None)
        fig.update_layout(legend_title_text= '')
        st.plotly_chart(fig)

    Home()
    graph()

with tab2:

    
    
    # Créer un DataFrame avec vos données
    data = {
    'Mouvement': ['Entrées', 'Sorties', 'Flux internes', 'Total'],
    '2014': [5956, 5952, 2534, 14442],
    '2015': [5099, 5102, 2397, 12598],
    '2016': [5053, 5258, 2625, 12936],
    '2017': [5678, 6130, 3242, 15050],
    '2018': [5699, 5871, 3455, 15025],
    '2021': [6625, 5717, 2637, 14979],
    'Evolution en 8 ans': [0.112324, -0.039483, 0.040647, 0.037183]
    }

    df = pd.DataFrame(data)
    #print(df)

    # Sélectionner les colonnes pertinentes pour le graphique
    df_evolution = df[['Mouvement', '2014', '2015', '2016', '2017', '2018', '2021']]

    # Transposer le DataFrame pour avoir l'année en index
    df_evolution = df_evolution.set_index('Mouvement').transpose()
    #print(df_evolution)

    # Utiliser Plotly Express pour créer le graphique
    figure = px.line(df_evolution, x=df_evolution.index, y=df_evolution.columns, 
                title="Flux de marchandises en Centre-Val-de-Loire (en million de tonnes-kilomètres)",
                markers= True,
                labels={"index": "Année", "value": "Nombre", "variable": "Mouvement"},
                )




    figure.update_yaxes(title_text= None)
    figure.update_xaxes(title_text= None)
    figure.update_layout(legend_title_text= '')
    # Positionnez la légende en bas
    figure.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="right", x=1))

    # Afficher le graphique
    st.plotly_chart(figure)

# Evolution  du volume de marchandises sur 6 ans
with tab3:   
    # Évolution du volume de marchandises échangées
    df_evolution_2015_2021= df[['Mouvement', 'Evolution en 8 ans']]

    df_evolution_2015_2021 = df[['Mouvement', 'Evolution en 8 ans']].copy()
    df_evolution_2015_2021.loc[:, 'Evolution en 8 ans'] *= 100

    # Arrondir la colonne "Evolution en 6 ans" à 2 décimales
    df_evolution_2015_2021['Evolution en 8 ans'] = df_evolution_2015_2021['Evolution en 8 ans'].round(2)


    # Utiliser Plotly Express pour créer le diagramme en barres
    figures = px.bar(df_evolution_2015_2021, x='Mouvement', y='Evolution en 8 ans',
            title="Taux d'évolution du transport routier de marchandises en Centre-Val-de-Loire 2015-2021 ",
            labels={"Evolution en 8 ans": "(%)"},
            text='Evolution en 8 ans',
            #color='Evolution en 6 ans',  # Couleur basée sur la valeur

    )
    figures.update_xaxes(title_text= None)

    # Afficher le diagramme en barres
    st.plotly_chart(figures)

#Top 5 des partenaires de la région Centre
with tab4:

    # Importer le jeu de données
    p= pd.read_csv("nouvelle_data/echange_centre_et_autres_regions.csv", delimiter=";")

    # Filtrer les lignes où la colonne 'Région' n'est pas égale à 'Total'
    ptri = p[p['Région'] != 'Total']
    ptri= ptri.drop(" Évolution 2021/2015", axis=1)


    # Melt pour transformer les colonnes "2015", "2016", etc. en colonnes "Année" et "Valeur"
    df_melted = pd.melt(ptri, id_vars=['Région'], var_name='Année', value_name='Valeur')

    # Convertir la colonne 'Valeur' en type numérique
    df_melted['Valeur'] = pd.to_numeric(df_melted['Valeur'], errors='coerce')

    # Agréger les données par région en utilisant la somme
    df_aggregated = df_melted.groupby(['Région']).agg({'Valeur': 'sum'}).reset_index()

    # Trier le DataFrame agrégé par la colonne 'Valeur' (somme)
    df_top5_regions = df_aggregated.sort_values(by='Valeur', ascending=False).head(5)

    # Filtrer le DataFrame original pour inclure seulement les régions du top 5
    df_top5 = df_melted[df_melted['Région'].isin(df_top5_regions['Région'])]

    # Création de l'histogramme pour le top 5
    fig = px.bar(df_top5, x='Année', y='Valeur', color='Région',
                labels={'Valeur': 'Valeur', 'Année': 'Année'},
                title='Top 5 des régions parténaires au Centre-Val-de-Loire 2015-2021',
                #text=df_top5['Valeur'].apply(lambda x: f'{x/1000:.0f}k'),
                template='plotly_white')

    # Mise en forme du graphique
    fig.update_layout(
        barmode='group',
        xaxis=dict(title=''),
        yaxis=dict(title=''),
        legend_title=''
    )
    # Enlever la grille
    fig.update_layout(yaxis_showgrid= False)

    # Affichage du graphique
    st.plotly_chart(fig)
