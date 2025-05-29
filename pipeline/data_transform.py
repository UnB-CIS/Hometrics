from typing import List, Dict, Any, Tuple, Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

class DataTransformer:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

  

    def transform_data(self) -> List[Dict[str, Any]]:
        return self.data
    
    def get_coordinates(self, address: str, max_retries: int = 1) -> Optional[Tuple[float, float]]:
        """
        Convert an address to latitude and longitude using Nominatim from geopy.
        
        Args:
            address: The address to geocode
            max_retries: Number of retries for technical errors only (timeouts, service errors)
        """
        geolocator = Nominatim(user_agent="house_price_project")
        
        # Try with different address formats
        address_formats = [
            # First try with the full context
            f"{address}, Brasília, DF, Brazil",
            # Then try with just the city and country
            f"{address}, Brasília, Brazil",
            # Finally try with just the neighborhood and city
            address
        ]
        
        for format_idx, full_address in enumerate(address_formats):
            print(f"Geocoding (format {format_idx+1}/{len(address_formats)}): {full_address}")
            
            try:
                # Single attempt for each format with no retries for not found addresses
                location = geolocator.geocode(full_address)
                
                if location:
                    print(f"Found location: {location.address} at {location.latitude}, {location.longitude}")
                    return (location.latitude, location.longitude)
                else:
                    print(f"No location found for '{full_address}', trying next format...")
            
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                # Only retry for technical errors, not for "not found"
                if max_retries > 1:
                    print(f"Geocoding error: {e}, retrying once...")
                    time.sleep(2)  # Wait before retry
                    try:
                        location = geolocator.geocode(full_address)
                        if location:
                            print(f"Found location on retry: {location.address} at {location.latitude}, {location.longitude}")
                            return (location.latitude, location.longitude)
                    except Exception:
                        pass
                print(f"Error geocoding address '{full_address}': {e}")
        
        # If we've tried all formats, try one more approach: split the address
        # This can help with addresses that have apartment numbers or other details
        if ', ' in address:
            try:
                # Try with just the first part before the first comma (usually the street address)
                parts = address.split(', ')
                if len(parts) > 1:
                    simplified_address = f"{parts[0]}, {parts[-1]}, Brasília, Brazil"
                    print(f"Trying simplified address: {simplified_address}")
                    
                    location = geolocator.geocode(simplified_address)
                    if location:
                        print(f"Found location with simplified address: {location.address} at {location.latitude}, {location.longitude}")
                        return (location.latitude, location.longitude)
            except Exception as e:
                print(f"Error with simplified address: {e}")
        
        print(f"Failed to geocode address: {address}")
        return None
    
    def add_coordinates_to_data(self, address_field: str, batch_size: int = 50, callback=None) -> List[Dict[str, Any]]:
        """
        Add latitude and longitude to each item in the data based on a specified address field.
        Processes data in batches of batch_size items and calls the callback function after each batch.
        
        Args:
            address_field: Field containing address to geocode
            batch_size: Number of items to process in each batch before calling callback
            callback: Optional function to call after each batch with the batch results
                      Should accept (batch_data, is_final_batch) as parameters
        """
        transformed_data = []
        total_items = len(self.data)
        current_batch = []
        
        print(f"Starting geocoding process for {total_items} items in batches of {batch_size}...")
        
        try:
            for i, item in enumerate(self.data):
                print(f"Processing item {i+1}/{total_items}...")
                
                if address_field in item and item[address_field]:
                    coordinates = self.get_coordinates(item[address_field])
                    
                    if coordinates:
                        item['latitude'] = coordinates[0]
                        item['longitude'] = coordinates[1]
                    else:
                        item['latitude'] = None
                        item['longitude'] = None
                else:
                    print(f"No valid address found in item {i+1}")
                    item['latitude'] = None
                    item['longitude'] = None
                    
                transformed_data.append(item)
                current_batch.append(item)
                
                # If we've completed a batch or this is the final item
                if len(current_batch) >= batch_size or i == total_items - 1:
                    batch_count = len(current_batch)
                    batch_with_coords = sum(1 for item in current_batch if item.get('latitude') is not None)
                    print(f"Batch complete: {batch_with_coords}/{batch_count} items have coordinates")
                    
                    # If a callback function was provided, call it with the current batch
                    if callback:
                        is_final_batch = (i == total_items - 1)
                        callback(current_batch, is_final_batch)
                    
                    # Reset the current batch
                    current_batch = []
                
                # Add a short delay to respect Nominatim's usage policy
                time.sleep(1)  # 1 second between requests
                
        except KeyboardInterrupt:
            print("\nGeocoding process was interrupted!")
            print(f"Processed {len(transformed_data)}/{total_items} items before interruption")
            
            # Save the current batch if there are items in it
            if current_batch and callback:
                print(f"Saving partial batch of {len(current_batch)} items...")
                callback(current_batch, True)  # Treat as final batch since we're stopping
            
            # Return the data processed so far
            return transformed_data
            
        # Print summary of geocoding
        with_coords = sum(1 for item in transformed_data if item.get('latitude') is not None)
        print(f"Geocoding complete: {with_coords}/{total_items} items have coordinates")
        
        return transformed_data
