import requests
from pathlib import Path
import logging
import time
import os
import concurrent.futures

from utils import filter_all_invoices_by_date, generate_csv, download_single_file, time_execution_counter

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
API_URL = os.getenv("API_URL", "https://rpachallengeocr.azurewebsites.net/seed")
BASE_URL = os.getenv("BASE_URL", "https://rpachallengeocr.azurewebsites.net/")
DOWNLOAD_FOLDER = Path(os.getenv("DOWNLOAD_FOLDER", "invoices"))
CSV_NAME = os.getenv("CSV_NAME", "filtered_invoices.csv")
TIMEOUT = int(os.getenv("TIMEOUT", 10))


def extract_data_from_api() -> list[dict]:
    """
    Extract data from the API Endpoint (discovered via DevTools)
    
    Returns
    -------
    list[dict]
        A list of dictionaries containing the extracted invoice data.
    """
    try: 
        logger.info(f"Making POST request to API: {API_URL}")
        response = requests.post(API_URL)
        response.raise_for_status()
        
        data_list = response.json()['data']
        logger.info(f"API returned {len(data_list)} records.")
        
        formatted_data = []
        for item in data_list:
            formatted_data.append({
                "ID": item['id'],
                "DueDate": item['duedate'],
                "URL": f"{BASE_URL}{item['invoice']}"
            })
        return formatted_data

    except requests.RequestException as e:
        logger.error(f"Error occurred while fetching API data: {e}")
        return []
    

def download_invoices_threading(invoices: list[dict]):
    DOWNLOAD_FOLDER.mkdir(exist_ok=True)
    
    if not invoices:
        logger.warning("Nenhuma fatura para baixar.")
        return
        
    logger.info(f"Iniciando o download de {len(invoices)} faturas em paralelo...")
    # Cria um pool de threads para executar os downloads.
    # O `with` garante que todas as threads terminem antes de continuar.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # `executor.map` aplica a função `download_single_file` a cada item
        # da lista `invoices`, distribuindo o trabalho entre as threads.
        executor.map(download_single_file, invoices, [DOWNLOAD_FOLDER]*len(invoices))


@time_execution_counter
def main():
    start = time.time()
    invoices = extract_data_from_api()
    filtered_invoices = filter_all_invoices_by_date(invoices)
    generate_csv(filtered_invoices, CSV_NAME)
    end = time.time()
    logger.info(f"Data extraction and processing completed in {end - start:.2f} seconds.")
    download_invoices_threading(filtered_invoices)


if __name__ == "__main__":
    main()