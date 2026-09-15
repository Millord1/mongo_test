import csv
import shutil
from pathlib import Path

import kagglehub
from dotenv import load_dotenv

from src.config.apis import KAGGLE_DATASET, DatasetNames

project_root = Path(__file__).resolve().parents[2]
data_dir = project_root / "data"
data_dir.mkdir(parents=True, exist_ok=True)
load_dotenv(project_root / ".env")


def get_expected_csv_filenames() -> set[str]:
    """Extrait la liste exacte des noms de fichiers définis dans l'enum DatasetNames."""
    return {dataset.value for dataset in DatasetNames}


def download_and_move_dataset() -> Path:
    """Télécharge le dataset depuis Kaggle et copie tous les fichiers CSV dans data_dir."""
    print("Téléchargement du dataset Kaggle...")

    try:
        cache_path = Path(kagglehub.dataset_download(KAGGLE_DATASET))
    except Exception as error:
        raise RuntimeError("Échec du téléchargement du dataset Kaggle.") from error

    csv_files = list(cache_path.rglob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"Aucun fichier CSV trouvé dans {cache_path}.")

    for csv_file in csv_files:
        target_file = data_dir / csv_file.name
        shutil.copy2(csv_file, target_file)
        print(f"Fichier copié : {target_file.name}")

    return data_dir


def clean_data_dir():
    """Supprime tous les fichiers CSV présents dans le dossier data_dir."""
    print(f"🧹 Nettoyage du dossier {data_dir}...")
    for file in data_dir.glob("*.csv"):
        file.unlink()


def ensure_csv_files_present():
    """Vérifie la présence exacte des 8 fichiers définis dans DatasetNames."""
    expected_filenames = get_expected_csv_filenames()
    existing_files = list(data_dir.glob("*.csv"))
    existing_filenames = {file.name for file in existing_files}

    if existing_filenames == expected_filenames:
        print(
            f"Les {len(expected_filenames)} fichiers CSV requis sont tous présents dans {data_dir}."
        )
        return

    print("Fichiers manquants ou invalides dans data/.")
    clean_data_dir()

    print("Téléchargement du dataset...")
    download_and_move_dataset()


def inspect_csv_headers():
    """Affiche les en-têtes de tous les fichiers CSV présents dans data/."""
    csv_files = sorted(list(data_dir.glob("*.csv")))

    if not csv_files:
        print("Aucun fichier CSV trouvé dans le dossier data.")
        return

    for file_path in csv_files:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            print(f"\n{file_path.name}")
            print(f"   Colonnes ({len(headers) if headers else 0}) : {headers}")
