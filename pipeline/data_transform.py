import os
import time
from typing import Any, Dict, List, Optional, Tuple

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import GoogleV3, Nominatim


class DataTransformer:
    def __init__(self, data: List[Dict[str, Any]], geocoding_service="nominatim"):
        self.data = data
        self.geocoding_service = geocoding_service.lower()

    def transform_data(self, skip_geocoding=False) -> List[Dict[str, Any]]:
        """Transform data and add coordinates if geocoding is enabled"""

        if not skip_geocoding:
            for item in self.data:
                if "full_address" in item and item["full_address"]:
                    coords = self.geocode_address(item["full_address"])
                    if coords:
                        item["latitude"] = coords[0]
                        item["longitude"] = coords[1]
                    else:
                        print(
                            f"Warning: Could not geocode address: {item['full_address']}"
                        )
                        # Set to None to indicate we tried but failed
                        item["latitude"] = None
                        item["longitude"] = None
        return self.data

    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Choose geocoding service based on configuration"""
        if self.geocoding_service == "google":
            return self.get_coordinates_google(address)
        else:  # Default to Nominatim
            return self.get_coordinates(address)

    def get_coordinates_google(
        self, address: str, max_retries: int = 2
    ) -> Optional[Tuple[float, float]]:
        """Convert an address to latitude and longitude using Google Maps API."""
        # Get API key from environment variables
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        if not api_key:
            print("Error: GOOGLE_MAPS_API_KEY not found in environment variables")
            return None

        geolocator = GoogleV3(api_key=api_key)

        # Try with different address formats
        address_formats = [
            # First try with the full context
            f"{address}, Brasília, DF, Brazil",
            # Then try with just the city and country
            f"{address}, Brasília, Brazil",
            # Finally try with just the address
            address,
        ]

        for format_idx, full_address in enumerate(address_formats):
            print(
                f"Google Geocoding (format {format_idx+1}/{len(address_formats)}): {full_address}"
            )

            try:
                # Attempt geocoding with a single API request
                location = geolocator.geocode(full_address)

                if location:
                    print(
                        f"Found location: {location.address} at {location.latitude}, {location.longitude}"
                    )
                    return (location.latitude, location.longitude)
                else:
                    print(
                        f"No location found for '{full_address}', trying next format..."
                    )

            except Exception as e:
                # Only retry for technical errors, not for "not found"
                if max_retries > 1:
                    print(f"Google geocoding error: {e}, retrying once...")
                    time.sleep(2)  # Wait before retry
                    try:
                        location = geolocator.geocode(full_address)
                        if location:
                            print(
                                f"Found location on retry: {location.address} at {location.latitude}, {location.longitude}"
                            )
                            return (location.latitude, location.longitude)
                    except Exception:
                        pass
                print(f"Error geocoding address '{full_address}': {e}")

        print(f"Failed to geocode address with Google API: {address}")
        return None

    def get_coordinates(
        self, address: str, max_retries: int = 2
    ) -> Optional[Tuple[float, float]]:
        """Convert an address to latitude and longitude using Nominatim from geopy (free service)."""
        geolocator = Nominatim(user_agent="house_price_project")

        # Try with different address formats
        address_formats = [
            # First try with the full context
            f"{address}, Brasília, DF, Brazil",
            # Then try with just the city and country
            f"{address}, Brasília, Brazil",
            # Finally try with just the neighborhood and city
            address,
        ]

        for format_idx, full_address in enumerate(address_formats):
            print(
                f"Geocoding (format {format_idx+1}/{len(address_formats)}): {full_address}"
            )

            try:
                # Single attempt for each format with no retries for not found addresses
                location = geolocator.geocode(full_address)

                if location:
                    print(
                        f"Found location: {location.address} at {location.latitude}, {location.longitude}"
                    )
                    return (location.latitude, location.longitude)
                else:
                    print(
                        f"No location found for '{full_address}', trying next format..."
                    )

            except (GeocoderTimedOut, GeocoderServiceError) as e:
                # Only retry for technical errors, not for "not found"
                if max_retries > 1:
                    print(f"Geocoding error: {e}, retrying once...")
                    time.sleep(2.2)  # Wait before retry
                    try:
                        location = geolocator.geocode(full_address)
                        if location:
                            print(
                                f"Found location on retry: {location.address} at {location.latitude}, {location.longitude}"
                            )
                            return (location.latitude, location.longitude)
                    except Exception:
                        pass
                print(f"Error geocoding address '{full_address}': {e}")

        if ", " in address:
            try:
                parts = address.split(", ")
                if len(parts) > 1:
                    simplified_address = f"{parts[0]}, {parts[-1]}, Brasília, Brazil"
                    print(f"Trying simplified address: {simplified_address}")

                    location = geolocator.geocode(simplified_address)
                    if location:
                        print(
                            f"Found location with simplified address: {location.address} at {location.latitude}, {location.longitude}"
                        )
                        return (location.latitude, location.longitude)
            except Exception as e:
                print(f"Error with simplified address: {e}")

        print(f"Failed to geocode address: {address}")
        return None

    def add_coordinates_to_data(
        self, address_field: str, batch_size: int = 50, callback=None
    ) -> List[Dict[str, Any]]:
        """
        Add latitude and longitude to each item in the data based on a specified address field.
        Processes data in batches of batch_size items and calls the callback function after each batch.
        """

        transformed_data = []
        total_items = len(self.data)
        current_batch = []

        print(
            f"Starting geocoding process for {total_items} items in batches of {batch_size}..."
        )

        try:
            for i, item in enumerate(self.data):
                print(f"Processing item {i+1}/{total_items}...")

                if address_field in item and item[address_field]:
                    coordinates = self.geocode_address(item[address_field])

                    if coordinates:
                        item["latitude"] = coordinates[0]
                        item["longitude"] = coordinates[1]
                    else:
                        item["latitude"] = None
                        item["longitude"] = None
                else:
                    print(f"No valid address found in item {i+1}")
                    item["latitude"] = None
                    item["longitude"] = None

                transformed_data.append(item)
                current_batch.append(item)

                # If we've completed a batch or this is the final item
                if len(current_batch) >= batch_size or i == total_items - 1:
                    batch_count = len(current_batch)
                    batch_with_coords = sum(
                        1 for item in current_batch if item.get("latitude") is not None
                    )
                    print(
                        f"Batch complete: {batch_with_coords}/{batch_count} items have coordinates"
                    )

                    # If a callback function was provided, call it with the current batch
                    if callback:
                        is_final_batch = i == total_items - 1
                        callback(current_batch, is_final_batch)

                    # Reset the current batch
                    current_batch = []

                # Add a short delay to respect Nominatim's usage policy
                time.sleep(2)  # 1 second between requests

        except KeyboardInterrupt:
            print("\nGeocoding process was interrupted!")
            print(
                f"Processed {len(transformed_data)}/{total_items} items before interruption"
            )

            # Save the current batch if there are items in it
            if current_batch and callback:
                print(f"Saving partial batch of {len(current_batch)} items...")
                callback(
                    current_batch, True
                )  # Treat as final batch since we're stopping

            # Return the data processed so far
            return transformed_data

        # Print summary of geocoding
        with_coords = sum(
            1 for item in transformed_data if item.get("latitude") is not None
        )
        print(f"Geocoding complete: {with_coords}/{total_items} items have coordinates")

        return transformed_data
