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




# Configuration de la page avec le titre, l'icône et le layout
st.set_page_config(page_title= "Dashboard", page_icon= "🌍", layout= "wide")

# Ajout d'un sous-titre utilisant le composant subheader de Streamlit
st.subheader("📊 Étude du marché dans le secteur du transport routier de marchandises en Centre-Val-de-Loire")

# Ajout d'un titre en utilisant le composant markdown de Streamlit
st.markdown("##")


# Création des pages en utilisant la fonction show_pages
show_pages(

        [
            
            Page("Home.py", "Entreprises de transport", "🚚"),
            Page("pages/Clients.py","Entreprises sollicitant le transport","🏭"),
            Page("pages/Types_de_marchandises.py", "Marchandises", "📦")
         
        ]
    )



# Création des onglets
tab1, tab2,tab3, = st.tabs(["Nombre de créations d'entreprises","Nombre de sièges d'entreprises et Parts des embauches", "Carte de localisation des entreprises"])


# Onglet 1: Entreprises par département
with tab1:
    
    # Importation du jeu de données 
    df= pd.read_excel("nouvelle_data/nouvelles_donnees_entrep_transp_marchandises-cef02.csv")
    df = df.query("Date_creation_etablissement != 2024")
    #df["Date_creation_etablissement"]= df["Date_creation_etablissement"].astype(int).astype(str)

    #st.dataframe(df)

    # la barre sur le coté
    #st.sidebar.image("Images/logo.png.png", caption= "Analyse concurrentielle")
    # Barre latérale avec filtres
    st.sidebar.header("Filtres")
    
    # Filtre sur de département
    Departement= st.sidebar.multiselect(
        "Selectionner un département",
        options= df["Departement_etablissement"].unique(),
        default= df["Departement_etablissement"].unique(),
        key="departement_key"  # Clé unique pour Departement
        )

    # Filtre sur la classe de l'établissement
    classe_etablissement=  st.sidebar.multiselect(
        "Selectionner une classe",
        options= df["Classe_etablissement"].unique(),
        default= df["Classe_etablissement"].unique(),
        key="Classe_key"  # Clé unique pour la classe_etablissement
        )

    # Filtre sur la date de création d'entreprises
    df["Date_creation_etablissement"] = pd.to_numeric(df["Date_creation_etablissement"], errors="coerce")
    annee = df["Date_creation_etablissement"].sort_values().unique()
    defaut = (2018, 2019, 2020, 2021, 2022, 2023)
    selected_years = st.sidebar.select_slider(
        "Sélectionner un intervalle d'années",
        options=annee,
        value=(defaut[0], defaut[-1])
        )


# Filtrer les données
    df_selection= df.query( 
        "Departement_etablissement == @Departement & Classe_etablissement == @classe_etablissement & Date_creation_etablissement >= @selected_years[0] & Date_creation_etablissement <= @selected_years[1]"
    )
    
    
    
    # Définir la fonction Home
    def Home():

        # Utilisation de l'expander pour créer une section dépliable
        with st.expander("Jeu de données"): 

            # Selection des colonnes à afficher à l'aide d'une liste déroulante multisélection
            showData= st.multiselect("Filtrer:", df_selection.columns, default=[])

            # Affichage des données sélectionnées dans un Dataframe
            st.write(df_selection[showData])

            st.subheader("Nombre de création d'entreprises", divider='rainbow')


        # KPI
        
        # Calcul du nombre d'entreprises par segment
        entreprises_interurbains = len(df_selection[df_selection["Classe_etablissement"] == "Transports routiers de fret interurbains"])
        entreprises_proximite = len(df_selection[df_selection["Classe_etablissement"] == "Transports routiers de fret de proximité"])
        entreprises_messagerie = len(df_selection[df_selection["Classe_etablissement"] == "Messagerie, fret express"])
        entreprises_affretement = len(df_selection[df_selection["Classe_etablissement"] == "Affrètement et organisation des transports"])
        
        # Création de 4 colonnes pour afficher les métriques
        total1, total2, total3,total4= st.columns(4, gap= "large")
        
        with total1:
            st.metric("Transports de fret interurbains",  entreprises_interurbains)
        with total2:
            st.metric("Transports de fret de proximité",  entreprises_proximite)
        with total3:    
            st.metric( "Messagerie,fret express",  entreprises_messagerie)
        with total4:
            st.metric("Affretement et organisation",  entreprises_affretement)
       
        #st.markdown("""---""")

        #style_metric_cards(background_color= "light blue", max_width=500)



   
    # Définir la fonction graph
    def graph():
        
        # Graphique 1: Évolution du nombre de création d'entreprises par  secteur

        # Regrouper le DataFrame df_selection par deux colonnes : "Classe_etablissement" et "Date_creation_etablissement". Ensuite il compte le nombre d'occurrences puis réinitialise l'index et renomme la colonne resultante en "Nombre_d_entreprises"
        evolution_entrep= df_selection.groupby(["Classe_etablissement", df_selection["Date_creation_etablissement"]]).size().reset_index(name='Nombre_d_entreprises')
        
        #palette_couleur= ['cyan','gris', 'marron','violet']
        palette_couleur= ['#d62728','#9467bd','#e377c2','#17becf']
        # Créer un graphique en courbe pour une creation d'entreprises
        fig_entre_par_an = px.line(evolution_entrep, x="Date_creation_etablissement", y="Nombre_d_entreprises", color="Classe_etablissement", markers= True,
                    orientation= "v",
                    title="Évolution du nombre de créations d'entreprises par segment",
                    labels={"Date_creation_etablissement": "Année", "Nombre_d_entreprises": ""},
                    text= "Nombre_d_entreprises",
                    color_discrete_sequence= palette_couleur,
                    # L'ordre d'apparition des catégories de la colonne "Classe_etablissement"
                    category_orders={"Classe_etablissement": ["Transports routiers de fret interurbains", "Transports routiers de fret de proximité", "Messagerie, fret express", "Affrètement et organisation des transports"]})
                
        # Positionnez la légende en bas
        fig_entre_par_an.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="right", x=1))
        # Supprimez l'en-tête de la légende
        fig_entre_par_an.update_layout(legend_title_text='')
        #Ne pas afficher le titre de l'axe des abcisses
        fig_entre_par_an.update_xaxes(title_text= None)
        # Ajustement de l'axe des ordonnées pour inclure une marge au dessus de la valeur maximale
        fig_entre_par_an.update_yaxes(range=[0, evolution_entrep["Nombre_d_entreprises"].max() + 10])
        



        # Graphique 2: La proportion de chaque secteur par departement

        # Création du DataFrame groupé par département et classe d'établissement
        df_grouped = df_selection.groupby(["Departement_etablissement", "Classe_etablissement"]).size().reset_index(name='Nombre_d_entreprises')
       
        # Calcul de la somme totale du nombre d'entreprises par département et ajoute cette info dans la colonne "Totale"
        df_grouped['Total'] = df_grouped.groupby("Departement_etablissement")["Nombre_d_entreprises"].transform('sum')

        # Calcul du pourcentage
        df_grouped['Pourcentage'] = (df_grouped['Nombre_d_entreprises'] / df_grouped['Total']) * 100

        # Définition d'une palette de couleurs pour les segments
        palette_couleur= ['#17becf','#e377c2', '#9467bd',  '#d62728']

        # Création d'un graphique à barres avce Plotly Express
        fig = px.bar(df_grouped, x="Departement_etablissement", y="Pourcentage",
                    color="Classe_etablissement", title="Proportion du nombre d'entreprises par département et par segment (en %)",
                    labels={"Pourcentage": "", "Departement_etablissement": "Département"},
                    text= round(df_grouped["Pourcentage"],2),
                    color_discrete_sequence=palette_couleur,  # Utilisez la palette "plotly" de Plotly Express
                    #Extraire des valeurs uniques dans l'ordre croissant
                    category_orders={"Classe_etablissement": sorted(df_grouped["Classe_etablissement"].unique())})
        # Positionnez la légende en bas
        fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="right", x=1))
        # Supprimez l'en-tête de la légende
        fig.update_layout(legend_title_text='')
        fig.update_xaxes(title_text= None)
        

        
        # Mettre les deux graphiques dans des containers
        col1,col2= st.columns(2)
        col1.plotly_chart(fig_entre_par_an, use_container_width= True)
        col2.plotly_chart(fig, use_container_width= True)

    
        
    Home()
    graph()   


# Onglets 2: Nombre de sièges d'entreprises et Parts des embauches dans les tous segments confondus     
with tab2:

    
    df_etab_siege = df.groupby(['Departement_etablissement', 'Etablissement_Siege']).size().reset_index(name='nombre_de_siege')
    palette_couleur= ["blue", "violet"]
    
    # Créer un graphique à barres empilées avec Plotly Express
    fig_ = px.bar(df_etab_siege, x='Departement_etablissement', y='nombre_de_siege', color='Etablissement_Siege',
                labels={'nombre_de_siege': 'Nombre d\'Établissements', 'Etablissement_Siege': 'Type d\'Établissement'},
                title='Nombre de sièges par segment et par de département',
                category_orders={'Departement_etablissement': df_etab_siege['Departement_etablissement'].unique()},
                color_discrete_sequence= palette_couleur,
                text= 'nombre_de_siege'
                
                )

    # Ajouter des étiquettes
    fig_.update_layout(xaxis_title='Département', yaxis_title='Nombre d\'Établissements')

    # cacher les étiquettes des axes
    fig_.update_xaxes(title= None)
    fig_.update_yaxes(title= None)

    # Cacher la legende
    fig_.update_layout(legend_title_text='')

    # Mettre la legende vers le bas
    # Positionnez la légende en bas
    fig_.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="left", x=0))

    # Afficher le graphique interactif
    #st.plotly_chart(figure)



    
    # Données des embauches 
    data = {
        'Taille d\'entreprise': ['0 à 9 salariés', '10 à 49 salariés', '50 à 250 salariés', '250+ salariés'],
        'Pourcentage': [67.8, 12.8, 12.9, 1.3]
    }

    # Palette de couleurs
    couleurs = px.colors.qualitative.Prism

    #couleurs = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    # Créer un camembert
    fig = px.pie(data, 
                values='Pourcentage', 
                names='Taille d\'entreprise', 
                title="Proportion du nombre d'embauches dans l\'entreposage et services auxiliaires en 2023",
                labels={'Pourcentage': 'Pourcentage'},
                hole=0.3,  # Taille du trou au milieu (0 à 1)
                color_discrete_sequence=couleurs,  # Utilisation de la palette de couleurs
                
                )
    fig.update_layout(legend=dict(orientation="h", y=-0.1, xanchor="right", x=1))

    # Afficher le camembert
    #st.plotly_chart(fig)
    
    # Mettre les deux graphiques dans des containers
    col1,col2= st.columns(2)
    col1.plotly_chart(fig_, use_container_width= True)
    col2.plotly_chart(fig, use_container_width= True)



# Réprsentation cartographique des entreprises de transport de marchandises
with tab3:
    
    # Supprimer les lignes avec des valeurs manquantes dans 'Latitude' et 'Longitude'
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
            popup_text = f"Nom de l'entreprise: {row['Denomination_unite_legale']}<br>Classe: {row['Classe_etablissement']}<br>Code_dept: {row['Code_departement_etablissement']}"

            # Ajouter un marqueur au groupe de marqueurs avec la popup personnalisée
            folium.Marker(location=[row['Latitude'], row['Longitude']], popup=popup_text).add_to(marker_cluster)

    # Afficher la carte dans Streamlit
    st.write("Localisation des entreprises de transport routier de marchandises en Centre-Val de Loire")
    folium_static(m)
    
  

    
    

   





