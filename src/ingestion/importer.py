import csv
import shutil
from pathlib import Path

import kagglehub
from dotenv import load_dotenv

from src.config.apis import KAGGLE_DATASET

project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env")

data_dir = project_root / "data"
data_dir.mkdir(parents=True, exist_ok=True)


def download_and_move_dataset() -> Path:
    """Download the Olist dataset from Kaggle and copy all CSV files to data_dir.

    Raises:
        RuntimeError: Download exception
        FileNotFoundError: If no CSV files are found

    Returns:
        Path: Path to the data directory containing all CSV files
    """

    if list(data_dir.glob("*.csv")):
        print(f"Fichiers CSV déjà présents dans : {data_dir}")
        return data_dir

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


def inspect_csv_headers():
    csv_files = sorted(list(data_dir.glob("*.csv")))

    if not csv_files:
        print("Aucun fichier CSV trouvé dans le dossier data.")
        return

    for file_path in csv_files:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            print(f"\n📄 {file_path.name}")
            print(f"   Colonnes ({len(headers) if headers else 0}) : {headers}")


if __name__ == "__main__":
    inspect_csv_headers()
