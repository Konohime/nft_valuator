import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Fonction pour obtenir les transactions pour une période donnée
def get_transactions_for_period(df, start_date, end_date, artist):
    return df[(df['timestamp'] >= start_date) & (df['timestamp'] < end_date) & (df['artist'] == artist)]['usd_price']

# Fonction pour calculer la moyenne des transactions
def calculate_average(transactions):
    return transactions.mean() if not transactions.empty else None

# Fonction pour obtenir la moyenne des trois dernières ventes
def get_last_three_sales_average(df, artist):
    last_three_sales = df[df['artist'] == artist].sort_values(by='timestamp', ascending=False).head(3)['usd_price']
    return last_three_sales.mean() if not last_three_sales.empty else None

# Titre de l'application
st.title("Évaluation des NFT")

# Télécharger les fichiers Excel
wallet_file = st.file_uploader("Télécharger le fichier wallet", type=["xlsx"])
sandbox_file = st.file_uploader("Télécharger le fichier sandbox_raw", type=["xlsx"])

# Entrée des dates
start_date = st.date_input("Date de début", datetime(2024, 4, 1))
end_date = st.date_input("Date de fin", datetime(2024, 7, 1))

if wallet_file and sandbox_file:
    # Charger les fichiers Excel
    wallet_df = pd.read_excel(wallet_file)
    sandbox_raw_df = pd.read_excel(sandbox_file)

    # Convertir la colonne timestamp en datetime
    sandbox_raw_df['timestamp'] = pd.to_datetime(sandbox_raw_df['timestamp'])

    # Initialiser les colonnes pour les moyennes USD
    wallet_df['artist_USD_avg'] = 0.0

    # Calculer les moyennes pour chaque ligne dans le wallet
    for index, row in wallet_df.iterrows():
        artist = row['artist']
        
        transactions = get_transactions_for_period(sandbox_raw_df, start_date, end_date, artist)
        artist_avg = calculate_average(transactions)
        
        if artist_avg is not None:
            wallet_df.at[index, 'artist_USD_avg'] = artist_avg
        else:
            last_three_avg = get_last_three_sales_average(sandbox_raw_df, artist)
            if last_three_avg is not None:
                wallet_df.at[index, 'artist_USD_avg'] = last_three_avg

    # Afficher le DataFrame résultant
    st.dataframe(wallet_df)

    # Bouton pour télécharger le fichier résultant
    output_file = st.text_input("Nom du fichier de sortie", "wallet_SR_valuated.xlsx")
    if st.button("Télécharger le fichier résultant"):
        wallet_df.to_excel(output_file, index=False)
        st.success(f"Fichier sauvegardé : {output_file}")
