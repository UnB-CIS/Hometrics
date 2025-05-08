from database.connection import MongoDBConnection
from database.repository import Property
from database.config import DB_URI
from pipeline.data_scraping import ScraperOrchestrator
from pipeline.data_cleaning import DataCleaner
from pipeline.data_transform import DataTransformer
from utils.data_handler import DataHandler
import pandas as pd
import os
import sys
import argparse
import time

def save_batch_callback(batch_data, is_final_batch):
    """
    Callback function to save batches of data as they are processed
    """
    print(f"\n===== SAVING BATCH OF {len(batch_data)} ITEMS =====")
    
    try:
        # Create a DataFrame from the batch data
        batch_df = pd.DataFrame(batch_data)
        
        # Split data by contract type
        rental_batch = batch_df[batch_df['contract_type'] == 'aluguel']
        sales_batch = batch_df[batch_df['contract_type'] == 'venda']
        
        print(f"Batch contains: {len(rental_batch)} rental properties, {len(sales_batch)} sales properties")
        
        # Define pipeline directory path
        pipeline_dir = os.path.join(os.getcwd(), 'pipeline')
        
        if not os.path.exists(pipeline_dir):
            os.makedirs(pipeline_dir)
        
        # Create DataHandler instance
        data_handler = DataHandler([])
        
        # Save rental data
        if not rental_batch.empty:
            rental_path = os.path.join(pipeline_dir, 'imoveis_aluguel_final.csv')
            print(f"Appending {len(rental_batch)} rental properties to {rental_path}...")
            try:
                data_handler.save_to_csv(
                    rental_batch, 
                    'imoveis_aluguel_final.csv', 
                    output_dir=pipeline_dir,
                    append=True  # Always append for batches
                )
                print(f"✓ Successfully saved rental batch")
            except Exception as e:
                print(f"ERROR saving rental batch: {str(e)}")
        
        # Save sales data
        if not sales_batch.empty:
            sales_path = os.path.join(pipeline_dir, 'imoveis_venda_final.csv')
            print(f"Appending {len(sales_batch)} sales properties to {sales_path}...")
            try:
                data_handler.save_to_csv(
                    sales_batch, 
                    'imoveis_venda_final.csv', 
                    output_dir=pipeline_dir,
                    append=True  # Always append for batches
                )
                print(f"✓ Successfully saved sales batch")
            except Exception as e:
                print(f"ERROR saving sales batch: {str(e)}")
        
        if is_final_batch:
            print("\n===== FINAL BATCH SAVED =====")
        
    except Exception as e:
        print(f"ERROR during batch saving: {str(e)}")


def load_and_process_data(csv_paths, standard_keys=None, skip_geocoding=False, batch_size=50, resume=False, restart=False):
    """
    Load CSV files, clean and transform data
    Processes data in batches and saves incrementally
    """
    all_data = []
    total_properties = 0
    
    print("\n===== LOADING DATA =====")
    # Load all CSV files and convert to list of dictionaries
    for csv_path in csv_paths:
        try:
            print(f"Loading file: {csv_path}...")
            df = pd.read_csv(csv_path)
            print(f"Found {len(df)} properties in {os.path.basename(csv_path)}")
            total_properties += len(df)
            
            # Convert DataFrame to list of dictionaries
            data_list = df.to_dict('records')
            all_data.extend(data_list)
        except Exception as e:
            print(f"ERROR loading {csv_path}: {str(e)}")
            continue
    
    print(f"\nTotal properties loaded: {len(all_data)} from {len(csv_paths)} files")
    
    # Clean data
    print("\n===== CLEANING DATA =====")
    if standard_keys is None:
        standard_keys = ['description', 'address', 'property_type', 'price', 'size', 
                         'bedrooms', 'bathrooms', 'parking_spaces', 'contract_type']
    
    print(f"Using standard keys: {standard_keys}")
    try:
        print("Removing duplicates and empty values...")
        cleaner = DataCleaner(all_data)
        cleaned_data = cleaner.clean_data(standard_keys)
        print(f"Data cleaning complete: {len(cleaned_data)} properties remaining (removed {len(all_data) - len(cleaned_data)} properties)")
    except Exception as e:
        print(f"ERROR during data cleaning: {str(e)}")
        return all_data  # Return original data if cleaning fails
    
    # Prepare for incremental saving
    pipeline_dir = os.path.join(os.getcwd(), 'pipeline')
    if not os.path.exists(pipeline_dir):
        os.makedirs(pipeline_dir)
    
    # Set up file paths
    rental_file_path = os.path.join(pipeline_dir, 'imoveis_aluguel_final.csv')
    sales_file_path = os.path.join(pipeline_dir, 'imoveis_venda_final.csv')
    
    # Check if we should resume processing or start fresh
    already_processed_items = {}
    if resume and not restart:
        # Try to load existing processed data
        try:
            if os.path.exists(rental_file_path):
                rental_df = pd.read_csv(rental_file_path)
                print(f"Found existing rental data with {len(rental_df)} items")
                # Create a dictionary of already processed items using the description as key
                for _, row in rental_df.iterrows():
                    already_processed_items[row['description']] = {
                        'file': 'rental',
                        'has_coords': pd.notnull(row.get('latitude')) and pd.notnull(row.get('longitude'))
                    }
            
            if os.path.exists(sales_file_path):
                sales_df = pd.read_csv(sales_file_path)
                print(f"Found existing sales data with {len(sales_df)} items")
                # Add sales items to the already processed dictionary
                for _, row in sales_df.iterrows():
                    already_processed_items[row['description']] = {
                        'file': 'sales',
                        'has_coords': pd.notnull(row.get('latitude')) and pd.notnull(row.get('longitude'))
                    }
            
            processed_count = len(already_processed_items)
            with_coords = sum(1 for info in already_processed_items.values() if info['has_coords'])
            print(f"Found {processed_count} already processed items ({with_coords} with coordinates)")
            
            if processed_count > 0:
                print("Will resume processing from where it left off")
                # Keep existing files for appending
            else:
                print("No previously processed items found, starting fresh")
                # Create empty files
                data_handler = DataHandler([])
                empty_df = pd.DataFrame(columns=standard_keys + ['latitude', 'longitude'])
                data_handler.save_to_csv(empty_df, 'imoveis_aluguel_final.csv', output_dir=pipeline_dir, append=False)
                data_handler.save_to_csv(empty_df, 'imoveis_venda_final.csv', output_dir=pipeline_dir, append=False)
                print("Created empty output files for batch processing")
        except Exception as e:
            print(f"Error loading existing data for resume: {str(e)}")
            print("Starting fresh instead")
            already_processed_items = {}
            # Create empty files
            data_handler = DataHandler([])
            empty_df = pd.DataFrame(columns=standard_keys + ['latitude', 'longitude'])
            data_handler.save_to_csv(empty_df, 'imoveis_aluguel_final.csv', output_dir=pipeline_dir, append=False)
            data_handler.save_to_csv(empty_df, 'imoveis_venda_final.csv', output_dir=pipeline_dir, append=False)
            print("Created empty output files for batch processing")
    else:
        # Clear existing output files (create empty files for appending)
        data_handler = DataHandler([])
        empty_df = pd.DataFrame(columns=standard_keys + ['latitude', 'longitude'])
        data_handler.save_to_csv(empty_df, 'imoveis_aluguel_final.csv', output_dir=pipeline_dir, append=False)
        data_handler.save_to_csv(empty_df, 'imoveis_venda_final.csv', output_dir=pipeline_dir, append=False)
        print("Created empty output files for batch processing")
    
    # Transform data
    print("\n===== TRANSFORMING DATA =====")
    if skip_geocoding:
        print("Geocoding skipped (--skip-geocoding flag used)")
        for item in cleaned_data:
            item['latitude'] = None
            item['longitude'] = None
        transformed_data = cleaned_data
        
        # Save all data at once if skipping geocoding
        save_batch_callback(transformed_data, True)
    else:
        try:
            print("Adding geographical coordinates based on description field...")
            print(f"Processing in batches of {batch_size} items")
            print("WARNING: This process may take a while and could be interrupted if Nominatim service is slow.")
            print("         Each batch of data will be saved as it completes.")
            print("         Use --skip-geocoding if you want to skip this step.")
            
            # Filter out already processed items with coordinates if resuming
            if resume and not restart and already_processed_items:
                # Filter the cleaned data to only include items that need processing
                need_processing = []
                skipped_count = 0
                for item in cleaned_data:
                    desc = item.get('description')
                    if desc in already_processed_items and already_processed_items[desc]['has_coords']:
                        # Skip this item since it already has coordinates
                        skipped_count += 1
                    else:
                        need_processing.append(item)
                
                print(f"Skipping {skipped_count} already processed items with coordinates")
                print(f"Processing {len(need_processing)} out of {len(cleaned_data)} total items")
                processing_data = need_processing
            else:
                processing_data = cleaned_data
            
            transformer = DataTransformer(processing_data)
            start_time = time.time()
            transformed_data = transformer.add_coordinates_to_data(
                'description',  # Use description field instead of address
                batch_size=batch_size,
                callback=save_batch_callback
            )
            elapsed_time = time.time() - start_time
            print(f"Transformation complete in {elapsed_time:.2f} seconds")
        except KeyboardInterrupt:
            print("\nGeocoding was interrupted by user. Continuing with partial results...")
            return cleaned_data  # Return cleaned data without coordinates
        except Exception as e:
            print(f"ERROR during transformation: {str(e)}")
            return cleaned_data  # Return cleaned data if transformation fails
    
    return transformed_data

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process property data, clean it, add coordinates, and save to CSV")
    parser.add_argument('--skip-geocoding', action='store_true', help="Skip the geocoding step (faster but no coordinates)")
    parser.add_argument('--verbose', '-v', action='store_true', help="Show more detailed output")
    parser.add_argument('--batch-size', type=int, default=50, help="Number of items to process before saving (default: 50)")
    parser.add_argument('--no-resume', action='store_true', help="Do not resume processing (start from beginning)")
    parser.add_argument('--restart', action='store_true', help="Force restart processing from beginning (same as --no-resume)")
    args = parser.parse_args()
    
    # Set resume to True by default (opposite of no-resume flag)
    args.resume = not args.no_resume and not args.restart
    
    return args

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    print("\n======= PROPERTY DATA PROCESSING PIPELINE =======\n")
    print(f"Skip Geocoding: {'YES' if args.skip_geocoding else 'NO'}")
    print(f"Verbose Mode: {'YES' if args.verbose else 'NO'}")
    print(f"Batch Size: {args.batch_size}")
    print(f"Resume Processing: {'YES (default)' if args.resume else 'NO (forced restart)'}")
    print(f"Force Restart: {'YES' if args.restart else 'NO'}")
    print(f"Auto-resume: Always enabled unless --restart or --no-resume is specified")
    
    # Define paths to CSV files
    dataset_dir = os.path.join(os.getcwd(), 'dataset', 'v02')
    csv_files = [
        os.path.join(dataset_dir, 'imoveis_aluguel.csv'),
        os.path.join(dataset_dir, 'imoveis_venda.csv')
    ]
    
    # Verify all files exist
    missing_files = [f for f in csv_files if not os.path.exists(f)]
    if missing_files:
        print(f"ERROR: The following input files could not be found:")
        for f in missing_files:
            print(f"  - {f}")
        sys.exit(1)
    
    # Process data
    try:
        processed_data = load_and_process_data(
            csv_files, 
            skip_geocoding=args.skip_geocoding,
            batch_size=args.batch_size,
            resume=args.resume,
            restart=args.restart
        )
    except Exception as e:
        print(f"Fatal error during data processing: {str(e)}")
        sys.exit(1)
    
    # Print sample of processed data
    if processed_data:
        print(f"\nProcessed {len(processed_data)} properties successfully")
        if args.verbose:
            print("\nSample property:")
            if processed_data:
                sample = processed_data[0]
                for key, value in sample.items():
                    print(f"{key}: {value}")
    
    # Summarize the already saved transformed data
    save_transformed_data(processed_data)

def save_transformed_data(data):
    """
    Since we're now saving in batches, this function is primarily used as a final summary
    of the overall process.
    """
    print("\n===== TRANSFORMED DATA SUMMARY =====")
    
    try:
        # Create a DataFrame from the data
        df = pd.DataFrame(data)
        
        # Split data by contract type
        rental_df = df[df['contract_type'] == 'aluguel']
        sales_df = df[df['contract_type'] == 'venda']
        
        print(f"Total properties processed: {len(df)}")
        print(f"  - Rental properties: {len(rental_df)}")
        print(f"  - Sales properties: {len(sales_df)}")
        
        # Count properties with coordinates
        with_coords = sum(1 for _, row in df.iterrows() if pd.notnull(row.get('latitude')))
        print(f"Properties with coordinates: {with_coords} / {len(df)} ({with_coords/len(df)*100:.1f}%)")
        
        # Define pipeline directory path for file info
        pipeline_dir = os.path.join(os.getcwd(), 'pipeline')
        rental_path = os.path.join(pipeline_dir, 'imoveis_aluguel_final.csv')
        sales_path = os.path.join(pipeline_dir, 'imoveis_venda_final.csv')
        
        # Get file sizes for reporting
        rental_size = os.path.getsize(rental_path) / 1024 if os.path.exists(rental_path) else 0
        sales_size = os.path.getsize(sales_path) / 1024 if os.path.exists(sales_path) else 0
        
        print(f"\nOutput files:")
        print(f"  - {rental_path} ({rental_size:.1f} KB)")
        print(f"  - {sales_path} ({sales_size:.1f} KB)")
            
        print("\n===== PROCESSING COMPLETE =====")
    except Exception as e:
        print(f"ERROR during summary process: {str(e)}")

if __name__ == "__main__":
    main()
