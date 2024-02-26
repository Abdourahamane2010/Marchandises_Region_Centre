import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from st_pages import Page, show_pages, add_page_title
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import style_metric_cards
from numerize.numerize import numerize
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# ce qui se met sur la fenetre du site
st.set_page_config(page_title= "Dashboard", page_icon= "🌍", layout= "wide")
st.subheader("📊 Étude du marché dans le secteur du transport routier de marchandises en Centre-Val-de-Loire")

st.markdown("##")


# Creation des pages
show_pages(
    [
        Page("Home.py", "Entreprises de transport", "🚚"),
        Page("pages/Clients.py","Entreprises sollicitant le transport","🏭"),
        Page("pages/Types_de_marchandises.py", "Marchandises", "📦"),
        
    ]
)

# Créer trois tables 
tab1, tab2,tab3, = st.tabs(["Nombre de création d'entreprises","Parts d'embauches par secteur", "Carte"])
with tab1:

    # Importer le jeu de données
    dataframe = pd.read_csv("nouvelle_data/nouvelles_donnees_clients_potentiels.csv", encoding='ISO-8859-1', sep=';')

    # Filtrer le DataFrame pour exclure les lignes où la date est égale à 2024
    dataframe = dataframe[dataframe["Date_creation_etablissement"] != 2024] 

    # Supprimer les NAN
    dataframe = dataframe.dropna(subset=["Date_creation_etablissement"])

    # Supprimer les lignes avec des valeurs manquantes dans 'Date_creation_etablissement'
    dataframe = dataframe.dropna(subset=["Date_creation_etablissement"])

    # Transfomer la colonne en numerique
    #dataframe["Date_creation_etablissement"] = pd.to_numeric(dataframe["Date_creation_etablissement"], errors="coerce")

    # Extraire l'année dans une nouvelle colonne 'Date_creation_etablissement'
    dataframe["Date_creation_etablissement"] = dataframe["Date_creation_etablissement"].astype("Int64")

    #Afficher le dataframe
    #st.dataframe(dataframe)
    # Sidebar
    st.sidebar.header("Filtres")

    departement_etablissement = st.sidebar.multiselect(
        "Selectionner un departement",
        options=dataframe["Departement_etablissement"].unique(),
        default=dataframe["Departement_etablissement"].unique()
    )


    sous_section_etablissement = st.sidebar.multiselect(
        "Selectionner un secteur",
        options=dataframe["Sous_section_etablissement"].unique(),
        default=dataframe["Sous_section_etablissement"].unique()
    )



    dataframe["Date_creation_etablissement"] = pd.to_numeric(dataframe["Date_creation_etablissement"], errors="coerce")
    annee = dataframe["Date_creation_etablissement"].sort_values().unique()
    defaut = (2018, 2019, 2020, 2021, 2022, 2023)
    selected_years = st.sidebar.select_slider(
        "Sélectionner un intervalle d'années",
        options=annee,
        value=(defaut[0], defaut[-1])
    )



    # Filtrer le DataFrame en fonction des filtres de la sidebar
    df_selection = dataframe.query(
        "Departement_etablissement==@departement_etablissement & Sous_section_etablissement==@sous_section_etablissement & Date_creation_etablissement >= @selected_years[0] & Date_creation_etablissement <= @selected_years[1]"
    )

    #st.dataframe(df_selection)

    def Home():
        with st.expander("Jeu de données"): 
            showData= st.multiselect("Filtrer:", df_selection.columns, default=[])
            st.write(df_selection[showData])


        
    #Créer des métriques

        comce_detail_hors_auto_moto= len(df_selection[df_selection["Sous_section_etablissement"] =="Commerce de détail, à l'exception des automobiles et des motocycles"])
        comce_gros_hors_auto_moto= len(df_selection[df_selection["Sous_section_etablissement"] == "Commerce de gros, à l'exception des automobiles et des motocycles"])
        autre_indus_manuf = len(df_selection[df_selection["Sous_section_etablissement"] == "Autres industries manufacturières"])
        

        total1, total2, total3= st.columns(3)
        with total1:
            st.metric("Commerce de gros hors auto et moto", comce_gros_hors_auto_moto)
        with total2:
            st.metric("Comerce de détail hors auto et moto", comce_detail_hors_auto_moto)
        with total3:    
            st.metric("Autres industries manufacturières", autre_indus_manuf)
        #style_metric_cards(background_color= "light blue")
        st.markdown("""---""")


    # Graphs

    def graph():

        #Graph1: Evolution du nombre de créations d'entreprises

        # Filtrer le DataFrame pour exclure les lignes avec "Fabrication de meubles"
        df_selection_filtered = df_selection.loc[df_selection["Sous_section_etablissement"] != "Fabrication de meubles"]
        # evolution de la creation  d'entreprises
        evolution_entrep= df_selection.groupby(["Sous_section_etablissement",  df_selection_filtered ["Date_creation_etablissement"]]).size().reset_index(name='Nombre_d_entreprises')

        # Palette de couleur
        palette_couleur= ['#17becf','#e377c2', '#9467bd']
        
        # Créer un graphique en courbe pour une creation d'entreprises
        fig_entre_par_an = px.line(evolution_entrep, x="Date_creation_etablissement", y="Nombre_d_entreprises", color="Sous_section_etablissement", markers= True,
                    orientation= "v",template="plotly_white",
                    title="Évolution du nombre de créations d'entreprises sollitant le transport de marchandises par secteur",
                    labels={"Date_creation_etablissement": "Année", "Nombre_d_entreprises": "Nombre d'entreprises"},
                    text= "Nombre_d_entreprises",
                    color_discrete_sequence=palette_couleur,
                    category_orders={"Sous_section_etablissement": ["Commerce de gros hors auto et moto", "Commerce de detail hors auto et moto, Autres industries manufacturières"]})
                
        # Positionnez la légende en bas
        fig_entre_par_an.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="right", x=1))
        # Supprimez l'en-tête de la légende
        fig_entre_par_an.update_layout(legend_title_text='')
        fig_entre_par_an.update_xaxes(title_text= None)
        fig_entre_par_an.update_yaxes(title_text= None)
        #fig_entre_par_an.update_layout(title_y=0.9)
        #st.plotly_chart(fig_entre_par_an)


    
        # Graph2: Poids de chaque dans le secteur par departement

        # Création du DataFrame groupé par département et classe d'établissement
        df_selection_filtered = df_selection.loc[df_selection["Sous_section_etablissement"] != "Fabrication de meubles"]

        df_grouped = df_selection_filtered.groupby(["Departement_etablissement", "Sous_section_etablissement"]).size().reset_index(name='Nombre_d_entreprises')
        # Calcul du total par département
        df_grouped['Total'] = df_grouped.groupby("Departement_etablissement")["Nombre_d_entreprises"].transform('sum')

        # Calcul du pourcentage
        df_grouped['Pourcentage'] = (df_grouped['Nombre_d_entreprises'] / df_grouped['Total']) * 100

        palette_couleur= ['#9467bd','#17becf','#e377c2']
        fig = px.bar(df_grouped, x="Departement_etablissement", y="Pourcentage",
                    color="Sous_section_etablissement", title="Poids du nombre d'entreprises département et par secteur (%)",
                    labels={"Pourcentage": "Pourcentage d'entreprises", "Departement_etablissement": "Département"},
                    text= round(df_grouped["Pourcentage"],2),
                    color_discrete_sequence=palette_couleur,  # Utilisez la palette "plotly" de Plotly Express
                    category_orders={"Sous_section_etablissement": sorted(df_grouped["Sous_section_etablissement"].unique())})
        # Positionnez la légende en bas
        fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="right", x=1))
        # Supprimez l'en-tête de la légende
        fig.update_layout(legend_title_text='')
        fig.update_xaxes(title_text= None)
        fig.update_yaxes(title_text= None)
        #fig.update_layout(title_y= 0.9)

        #st.plotly_chart(fig)
        
        left,right= st.columns(2)
        left.plotly_chart(fig_entre_par_an, use_container_width= True)
        right.plotly_chart(fig, use_container_width= True)

    Home()
    graph()



# Créer la table pour les parts des embauches 
with tab2:

    
    
    # Données des embuaches dans le secteur du commerce de detail, à l'exception de l'automobile
    data = {
        'Taille d\'entreprise': ['0 à 9 salariés', '10 à 49 salariés', '50 à 250 salariés', '250+ salariés'],
        'Pourcentage': [76.0, 10.5, 7.9, 0.1]
    }

    # Palette de couleurs
    couleurs = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    # Créer un camembert
    fig = px.pie(data, 
                values='Pourcentage', 
                names='Taille d\'entreprise', 
                title='Répartition des embauches dans le secteur de commerce de détail, hors autos et motos en 2023',
                labels={'Pourcentage': 'Pourcentage'},
                hover_data=['Pourcentage'],
                hole=0.3,  # Taille du trou au milieu (0 à 1)
                color_discrete_sequence=couleurs # Utilisation de la palette de couleurs,
            
                )


    # Afficher le camembert
    st.plotly_chart(fig)


    # Données
    data = {
        'Taille d\'entreprise': ['0 à 9 salariés', '10 à 49 salariés', '50 à 250 salariés', '250+ salariés'],
        'Pourcentage': [74.1, 17.3, 4.3, 0.4]
    }

    # Palette de couleurs
    couleurs = ['blue', 'violet', 'pink', 'orange']

    # Créer un camembert
    fig = px.pie(data, 
                values='Pourcentage', 
                names='Taille d\'entreprise', 
                title='Répartition des embauches dans le secteur de commerce de gros, hors autos et motos en 2023',
                labels={'Pourcentage': 'Pourcentage'},
                hover_data=['Pourcentage'],
                hole=0.3,  # Taille du trou au milieu (0 à 1)
                color_discrete_sequence=couleurs  # Utilisation de la palette de couleurs
                )

    # Afficher le camembert
    st.plotly_chart(fig)


    # Données
    data = {
        'Taille d\'entreprise': ['0 à 9 salariés', '10 à 49 salariés', '50 à 250 salariés', '250+ salariés'],
        'Pourcentage': [77.8, 6.8, 7.7, 5.3]
    }

    # Palette de couleurs
    couleurs = px.colors.qualitative.Plotly
    #couleurs = ['#2ca02c', '#d62728', '#9467bd', '#ff7f0e']

    # Créer un camembert
    fig = px.pie(data, 
                values='Pourcentage', 
                names='Taille d\'entreprise', 
                title='Répartition des embauches dans le secteur Autres industries manufacturières en 2023',
                labels={'Pourcentage': 'Pourcentage'},
                hole=0.3,  # Taille du trou au milieu (0 à 1)
                color_discrete_sequence=couleurs,  # Utilisation de la palette de couleurs
    )

    # Afficher le camembert
    st.plotly_chart(fig)



# Créer la table pour la carte 
with tab3:
    df_selection = df_selection.dropna(subset=['Latitude', 'Longitude'])

    # Créer une carte Folium
    m = folium.Map(location=[47.4239, 0.6778], zoom_start=8, control_scale=True)

    # Créer un groupe de marqueurs pour regrouper les marqueurs sur la carte
    marker_cluster = MarkerCluster().add_to(m)
    # Créer un cluster de marqueurs pour chaque département
    dept_cluster = MarkerCluster().add_to(m)

    # Filtrer les entreprises par département et classe_etablissement
    departements = df_selection['Departement_etablissement'].unique()

    for departement in departements:
        df_dept = df_selection[df_selection['Departement_etablissement'] == departement]

        for index, row in df_dept.iterrows():
            # Construire le texte de la popup
            popup_text = f"Nom de l'entreprise: {row['Denomination_usuelle_etablissement']}<br>Classe: {row['Sous_section_etablissement']}<br>Code_dept: {row['Code_departement_etablissement']}"

            # Ajouter un marqueur au groupe de marqueurs avec la popup personnalisée
            folium.Marker(location=[row['Latitude'], row['Longitude']], popup=popup_text).add_to(marker_cluster)

    # Afficher la carte dans Streamlit
    st.header("Carte des Entreprises en Centre-Val de Loire")
    folium_static(m)