import concurrent.futures
import os
import random
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Define headers for requests to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"
}


def clean_description(text):
    """Clean up the description text by removing extra whitespace and tabs"""
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\t", " ")
    text = text.strip()
    return text


def fetch_property_description(url, headers, max_retries=3):
    """
    Fetch and extract the description for a single property with retry logic
    """
    retries = 0
    backoff_factor = 2
    base_wait_time = 2

    while retries <= max_retries:
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                # Parse the HTML content
                property_soup = BeautifulSoup(response.text, "html.parser")

                # Find the description elements
                description_elements = property_soup.find_all(
                    "p", class_="texto-descricao"
                )

                if description_elements:
                    # Extract and clean the description text from all matching elements
                    full_description = " ".join(
                        [clean_description(elem.text) for elem in description_elements]
                    )
                    return full_description, "success"
                else:
                    return "", "no_description"

            elif response.status_code == 429:  # Too many requests
                retries += 1
                jitter = random.uniform(0.5, 1.5)
                wait_time = base_wait_time * (backoff_factor**retries) * jitter
                time.sleep(wait_time)
                continue

            elif response.status_code >= 500:  # Server error
                retries += 1
                jitter = random.uniform(0.5, 1.5)
                wait_time = base_wait_time * (backoff_factor**retries) * jitter
                time.sleep(wait_time)
                continue

            else:
                return "", f"http_error_{response.status_code}"

        except Exception as e:
            retries += 1
            if retries <= max_retries:
                jitter = random.uniform(0.5, 1.5)
                wait_time = base_wait_time * (backoff_factor**retries) * jitter
                time.sleep(wait_time)
                continue
            return "", f"exception_{str(e)}"

    return "", "max_retries_reached"


def extract_property_descriptions(
    category,
    tsv_filename=None,
    output_dir=None,
    delay_min=0.2,
    delay_max=0.5,
    max_properties=None,
    workers=6,
    batch_size=50,
    save_each_batch=True,
):
    """
    Extract property descriptions from all listings in a TSV file using concurrent processing
    """

    if tsv_filename is None:
        tsv_filename = f"imoveis_df_{category}.tsv"

    tsv_file_path = os.path.join(
        "scripts/df-imoveis/dataset/raw_listings", tsv_filename
    )

    if output_dir is None:
        output_dir = "scripts/df-imoveis/dataset/detailed_properties"

    os.makedirs(output_dir, exist_ok=True)

    output_file_path = os.path.join(output_dir, f"imoveis_df_{category}.tsv")

    if not os.path.exists(tsv_file_path):
        print(f"Error: TSV file not found at {tsv_file_path}")
        return

    print(f"Reading properties from {tsv_file_path}")

    try:

        df = pd.read_csv(tsv_file_path, sep="\t")

        if df.empty:
            print("No properties found in the TSV file.")
            return

        # Get the total number of properties to process
        total_properties = len(df)
        if max_properties and max_properties < total_properties:
            print(
                f"Limiting processing to {max_properties} out of {total_properties} properties"
            )
            df = df.head(max_properties)
            total_properties = max_properties
        else:
            print(f"Found {total_properties} properties in the TSV file")

        if "description" not in df.columns:
            df["description"] = ""

        success_count = 0
        failure_count = 0

        num_batches = (
            total_properties + batch_size - 1
        ) // batch_size  # Ceiling division

        for batch_idx in range(num_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, total_properties)
            batch_df = df.iloc[start_idx:end_idx].copy()

            print(
                f"\nProcessing batch {batch_idx+1}/{num_batches} (properties {start_idx+1} to {end_idx})..."
            )

            batch_results = []
            batch_indices = []

            urls = [(i, row.iloc[0]) for i, row in batch_df.iterrows()]
            # Shuffle order for more human-like behavior
            random.shuffle(urls)

            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                # List of user agents for randomization
                USER_AGENTS = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
                ]
                # Submit all tasks, randomizing headers
                future_to_idx = {}
                for idx, url in urls:
                    headers = HEADERS.copy()
                    headers["User-Agent"] = random.choice(USER_AGENTS)
                    future = executor.submit(fetch_property_description, url, headers)
                    future_to_idx[future] = (idx, url)

                # Micro-pause logic
                processed_count = 0
                pause_every = random.randint(10, 30)
                for future in tqdm(
                    concurrent.futures.as_completed(future_to_idx),
                    total=len(future_to_idx),
                    desc="Processing properties",
                ):
                    idx, url = future_to_idx[future]
                    try:
                        description, status = future.result()
                        batch_indices.append(idx)

                        # Extra retry for empty/None descriptions
                        if (
                            not description or description.strip() == ""
                        ) and status == "success":
                            print(
                                f"[WARN] Empty description for idx {idx}, url: {url}. Retrying after 10s..."
                            )
                            time.sleep(10)
                            description_retry, status_retry = (
                                fetch_property_description(url, HEADERS)
                            )
                            if description_retry and description_retry.strip() != "":
                                description = description_retry
                                status = status_retry
                                print(f"[INFO] Retry succeeded for idx {idx}")
                            else:
                                print(
                                    f"[ERROR] Still empty after retry for idx {idx}, url: {url}"
                                )

                        if (
                            status == "success"
                            and description
                            and description.strip() != ""
                        ):
                            batch_results.append((idx, description))
                            success_count += 1
                        else:
                            print(
                                f"[ERROR] Failed to fetch description for idx {idx}, url: {url}, status: {status}"
                            )
                            failure_count += 1
                    except Exception as e:
                        print(f"Error processing property at {url}: {str(e)}")
                        failure_count += 1

                    processed_count += 1
                    if processed_count % pause_every == 0:
                        micro_pause = random.uniform(1, 4)
                        print(
                            f"[HUMAN-LIKE] Pausing for {micro_pause:.2f}s to look at details..."
                        )
                        time.sleep(micro_pause)
                        pause_every = random.randint(15, 40)

            for idx, description in batch_results:
                df.at[idx, "description"] = description

            if save_each_batch:
                temp_output_path = os.path.join(
                    output_dir, f"imoveis_df_{category}.tsv"
                )
                df.to_csv(temp_output_path, sep="\t", index=False)
                print(f"Saved interim results to {temp_output_path}")

            if batch_idx < num_batches - 1:
                batch_delay = random.lognormvariate(
                    2.5, 0.4
                )  # mean ~12s, still with some jitter
                print(
                    f"[HUMAN-LIKE] Waiting {batch_delay:.2f} seconds before next batch..."
                )
                time.sleep(batch_delay)

        # Save the final updated dataframe to the output file
        df.to_csv(output_file_path, sep="\t", index=False)

        print("\n=============================================")
        print(f"Processing complete!")
        print(f"Successfully processed: {success_count} properties")
        print(f"Failed to process: {failure_count} properties")
        print(f"Output saved to: {output_file_path}")
        print("=============================================")

        return output_file_path

    except Exception as e:
        print(f"Error processing TSV file: {str(e)}")
        return None


if __name__ == "__main__":
    # Example usage
    categories = ["aluguel", "venda"]

    for category in categories:
        extract_property_descriptions(
            category=category,
            delay_min=1.0,  # faster per-request minimum delay
            delay_max=2.0,  # faster per-request maximum delay
            workers=6,  # more parallel workers
            batch_size=250,  # keep batch size
            save_each_batch=True,
        )
