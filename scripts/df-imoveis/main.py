import time
from property_descriptions import extract_property_descriptions
from property_scraper import PropertyScraper
from scraping_utils import PROPERTY_TYPES

from scripts.utils.data_handler import DataHandler
from scripts.utils.data_cleaner import clean_duplicates


HEADERS = {
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"
}

BASE_URL_ALUGUEL = "https://www.dfimoveis.com.br/aluguel/df/todos/{property_type}?pagina="
BASE_URL_VENDA = "https://www.dfimoveis.com.br/venda/df/todos/{property_type}?pagina="


def run_scraper(
    category="venda",
    property_type="imoveis",
    max_pages=30,
    workers=3,
    output_dir=None,
    append=True,
    custom_output_files=None,
    batch_size=30,
    batch_delay=30,
    save_each_batch=True,
):
    """Executa o raspador do DF Imóveis com os parâmetros especificados."""

    base_url = BASE_URL_ALUGUEL if category == "aluguel" else BASE_URL_VENDA

    scraper = PropertyScraper(
        base_url=base_url, property_type=property_type, headers=HEADERS
    )
    properties_data = scraper.scrape_all_pages(
        max_pages=max_pages,
        workers=workers,
        batch_size=batch_size,
        batch_delay=batch_delay,
        save_each_batch=save_each_batch,
        category=category,
        property_type=property_type,
        output_dir=output_dir,
        append=append,
    )

    data_handler = DataHandler(properties_data)
    df = data_handler.create_dataframe(category)

    if output_dir is not None:
        if (
            custom_output_files
            and "excel_path" in custom_output_files
            and "tsv_path" in custom_output_files
        ):
            excel_path = custom_output_files["excel_path"]
            tsv_path = custom_output_files["tsv_path"]

            # Salva diretamente nos caminhos especificados
            data_handler.save_to_excel(df, excel_path, append=append)
            data_handler.save_to_tsv(df, tsv_path, append=append)

            print(f"Excel data saved to {excel_path}")
            print(f"TSV data saved to {tsv_path}")
        else:
            excel_filename = f"imoveis_df_{category}.xlsx"
            tsv_filename = f"imoveis_df_{category}.tsv"

            data_handler.save_to_excel(
                df, excel_filename, output_dir=output_dir, append=append
            )
            data_handler.save_to_tsv(
                df, tsv_filename, output_dir=output_dir, append=append
            )

            print(f"Excel data saved to {output_dir}/{excel_filename}")
            print(f"TSV data saved to {output_dir}/{tsv_filename}")

    return df


def run_all_scrapers(
    max_pages=30,
    workers=3,
    output_dir=None,
    append=True,
    batch_size=30,
    batch_delay=30,
    save_each_batch=True,
):
    """Executa todos os raspadores para todos os tipos de contrato e tipos de propriedade."""
    contract_types = [
        "aluguel",
        "venda",
    ]
    all_dataframes = []

    for contract_type in contract_types:
        for property_type in PROPERTY_TYPES:
            print(f"\n\nScraping {contract_type} - {property_type}...")
            df = run_scraper(
                category=contract_type,
                property_type=property_type,
                max_pages=max_pages,
                workers=workers,
                output_dir=output_dir,
                append=append,
                batch_size=batch_size,
                batch_delay=batch_delay,
                save_each_batch=save_each_batch,
            )
            all_dataframes.append(df)

            time.sleep(30)

    return all_dataframes


if __name__ == "__main__":

    # run_scraper(
    #     category='venda',
    #     property_type='apartamento',
    #     max_pages=1,
    #     workers=3,
    #     output_dir="scripts/df-imoveis/dataset/raw_listings",
    #     append=True,
    #     batch_size=30,
    #     batch_delay=30,
    #     save_each_batch=True
    # )

    run_all_scrapers(
        max_pages=None,
        workers=6,
        output_dir="scripts/df-imoveis/dataset/raw_listings",
        append=True,
        batch_size=45,
        batch_delay=15,
        save_each_batch=True,
    )

    clean_duplicates(
        input_dir="scripts/df-imoveis/dataset/raw_listings",
        output_dir="scripts/df-imoveis/dataset/raw_listings",
    )

    categories = ["aluguel", "venda"]

    for category in categories:
        extract_property_descriptions(
            category=category,
            delay_min=0.5,
            delay_max=2,
            workers=2,
            batch_size=10,
            save_each_batch=True,
        )
