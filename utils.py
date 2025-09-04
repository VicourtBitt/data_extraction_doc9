from datetime import datetime
from pathlib import Path
import requests
import pandas as pd
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def filter_all_invoices_by_date(invoices: list[dict]):
    """
    Filter the invoices to see if the DueDate is indeed today or if it
    has already passed

    Parameters
    ----------
    invoices : list[dict]
        The list of invoice data to filter

    Returns
    -------
    list[dict]
        The filtered list of invoices
    """
    today = datetime.now()
    filtered_list = []
    
    for invoice in invoices:
        due_date = datetime.strptime(invoice["DueDate"], "%d-%m-%Y")
        if due_date <= today:
            filtered_list.append(invoice)

    logger.info(f"Filtered invoices by date: {len(filtered_list)} out of {len(invoices)}.")
    return filtered_list


def generate_csv(data: list[dict], csv_name: str):
    """
    Generate a CSV file with the filtered invoice data using pandas (personal choice)

    Parameters
    ----------
    data : list[dict]
        The list of filtered invoice data to write to CSV
    """
    if not data:
        logger.warning("No data available to generate CSV.")
        return
    
    try:
        df = pd.DataFrame(data)
        # Granting order and only relevant columns
        df = df[["ID", "DueDate", "URL"]] 
        df.to_csv(csv_name, index=False, encoding='utf-8')
        logger.info(f"CSV file generated successfully: {csv_name}")

    except Exception as e:
        logger.error(f"Error occurred while generating CSV: {e}")


def download_invoices(invoices: list[dict], path: Path):
    """
    Download the invoices images into a local directory

    Parameters
    ----------
    invoices : list[dict]
        The list of invoice data to download
    """
    # Create the download folder if it doesn't exist
    path.mkdir(exist_ok=True)

    if not invoices:
        logger.warning("No invoices available for download.")
        return
    
    logger.info(f"Starting download of {len(invoices)} invoices...")
    for invoice in invoices:
        try:
            # Get the URL from the specific object/dict
            response = requests.get(invoice["URL"])
            response.raise_for_status()

            # Save the invoice image to the download folder
            invoice_path = f"{path}/{invoice['ID']}.jpg"

            with open(invoice_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Downloaded invoice: {invoice['ID']}")

        except requests.RequestException as e:
            logger.error(f"Error occurred while downloading invoice {invoice['ID']}: {e}")


def download_single_file(invoice, path: Path):
    """
    Download a single invoice file.

    Parameters
    ----------
    invoice : dict
        The invoice data containing the URL and ID.
    path : Path
        The local directory path to save the downloaded file.
    """
    try:
        url = invoice['URL']
        response = requests.get(url, timeout=10) # Adiciona um timeout
        response.raise_for_status()
        
        file_path = f"{path}/{invoice['ID']}.jpg"

        with open(file_path, "wb") as f:
            f.write(response.content)
        # Log de sucesso para cada arquivo individual
        logger.info(f"Download concluído: {invoice['ID']}")
        return f"Sucesso: {file_path}"

    except requests.RequestException as e:
        logger.error(f"Falha ao baixar {url}: {e}")
        return f"Falha: {url}"


def time_execution_counter(func):
    """
    Decorator to measure the execution time of a function.

    Parameters
    ----------
    func : callable
        The function to measure the execution time for

    Returns
    -------
    wrapper : callable
        The wrapped function with execution time measurement
    """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logger.info(f"Execution time for {func.__name__}: {execution_time:.4f} seconds")
        return result
    return wrapper