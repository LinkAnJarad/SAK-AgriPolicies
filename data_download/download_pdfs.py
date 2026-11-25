import pandas as pd 
from tqdm import tqdm
import requests

FAOLEX_CSV = 'data_download/faolex-export.csv'

faolex_df = pd.read_csv(FAOLEX_CSV)

ph_idx = faolex_df["Jurisdiction"] == "Philippines"
faolex_ph = faolex_df[ph_idx]

faolex_ph.to_csv('data_download/faolex-ph.csv', index=False)

print("Downloading from FAOLEX...")

for i, entry in tqdm(faolex_ph.iterrows()):
    pdf_link = entry["PDF Link"]
    response = requests.get(pdf_link)
    response.raise_for_status()

    faolex_id = entry["FAOLEX ID"]

    with open(f"documents_raw/{faolex_id}.pdf", "wb") as pdf_file:
        pdf_file.write(response.content)
