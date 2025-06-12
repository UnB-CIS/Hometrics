import os
import pandas as pd
import glob

def clean_duplicates(input_dir, output_dir):
    """
    Clean duplicates from all TSV files in the specified directory.
    """

    # Find all TSV files in the input directory
    tsv_files = glob.glob(os.path.join(input_dir, "*.tsv"))
    
    if not tsv_files:
        print(f"No TSV files found in {input_dir}")
        return
    
    print(f"Found {len(tsv_files)} TSV files to process")
    
    for file_path in tsv_files:
        file_name = os.path.basename(file_path)
        print(f"\nProcessing {file_name}...")
        
        try:
            # Read the TSV file
            df = pd.read_csv(file_path, sep='\t')
            
            # Get the initial row count
            initial_count = len(df)
            print(f"Initial row count: {initial_count}")
            
            # Remove duplicates
            # Assuming the first column is the URL and we want to keep the first occurrence
            df.drop_duplicates(subset=df.columns[0], keep='first', inplace=True)
            
            # Get the final row count
            final_count = len(df)
            print(f"Final row count: {final_count}")
            print(f"Removed {initial_count - final_count} duplicate entries")
            
            
            # Save the cleaned dataframe
            output_path = os.path.join(output_dir, file_name)
            df.to_csv(output_path, sep='\t', index=False)
            print(f"Cleaned file saved to {output_path}")
            
        except Exception as e:
            print(f"Error processing {file_name}: {str(e)}")
    
    print("\nDuplicate cleaning completed!")



if __name__ == "__main__":
    # First clean duplicates within each file
    print("=== STEP 1: Cleaning duplicates within each file ===")
    clean_duplicates(input_dir="scripts/df-imoveis/dataset/raw_listings", output_dir="scripts/df-imoveis/dataset/raw_listings")
    