import requests
from datetime import datetime
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

credentials = {
    "librelink": {
        "username": os.getenv("LIBRELINK_USERNAME"),
        "password": os.getenv("LIBRELINK_PASSWORD"),
        "region": os.getenv("LIBRELINK_REGION", "EU")
    },
    "nightscout": {
        "url": os.getenv("NIGHTSCOUT_URL"),
        "api_token": os.getenv("NIGHTSCOUT_API_TOKEN")
    }
}

class LibreLinkUploader:
    def __init__(self, credentials: dict):
        """Initialize with credentials dictionary."""
        self.config = credentials
        self.libre_session = requests.Session()
        self.nightscout_session = requests.Session()
        
    def authenticate(self) -> None:
        """Authenticate with LibreLink Up API."""
        headers = {
            "User-Agent": "LibreLinkUp",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Product": "llu.android",
            "Version": "4.7.0"
        }
        
        data = {
            "email": self.config["librelink"]["username"],
            "password": self.config["librelink"]["password"]
        }
        
        region = self.config["librelink"]["region"].lower()
        url = f"https://api-{region}.libreview.io/llu/auth/login"
        
        try:
            response = self.libre_session.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            auth_data = response.json()
            if 'data' not in auth_data:
                error_msg = auth_data.get('message', 'Unknown error')
                raise Exception(f"Authentication failed: {error_msg}")
            
            self.auth_token = auth_data["data"]["authTicket"]["token"]
            self.libre_session.headers.update({
                "Authorization": f"Bearer {self.auth_token}",
                "User-Agent": "LibreLinkUp",
                "Product": "llu.android",
                "Version": "4.7.0"
            })
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error during authentication: {str(e)}")
        except Exception as e:
            raise Exception(f"Authentication error: {str(e)}")

    def get_glucose_data(self) -> list:
        """Get latest glucose readings from LibreLink Up API."""
        region = self.config['librelink']['region'].lower()
        url = f"https://api-{region}.libreview.io/llu/connections"
        
        try:
            # First, get the patient ID
            response = self.libre_session.get(url)
            response.raise_for_status()
            
            connections_data = response.json()
            if not connections_data or not isinstance(connections_data, dict) or 'data' not in connections_data:
                raise Exception("Invalid connections response format")
            
            connections = connections_data['data']
            if not connections or not isinstance(connections, list) or len(connections) == 0:
                raise Exception("No patient connections found")
            
            # Get the first patient ID
            patient_id = connections[0]['patientId']
            
            # Get the glucose data for this patient
            glucose_url = f"https://api-{region}.libreview.io/llu/connections/{patient_id}/graph"
            glucose_response = self.libre_session.get(glucose_url)
            glucose_response.raise_for_status()
            
            glucose_data = glucose_response.json()
            if not isinstance(glucose_data, dict) or 'data' not in glucose_data:
                raise Exception("Invalid glucose data response format")
            
            # Extract the glucose readings
            readings = []
            if 'connection' in glucose_data['data']:
                connection = glucose_data['data']['connection']
                if 'glucoseMeasurement' in connection:
                    measurement = connection['glucoseMeasurement']
                    reading = {
                        "Timestamp": measurement.get('FactoryTimestamp', measurement.get('RecordedTime')),
                        "ValueInMgPerDl": measurement.get('ValueInMgPerDl', measurement.get('Value')),
                        "TrendArrow": measurement.get('TrendArrow', measurement.get('trend'))
                    }
                    readings.append(reading)
                
                # Add historical data if available
                if 'graphData' in glucose_data['data']:
                    for entry in glucose_data['data']['graphData']:
                        reading = {
                            "Timestamp": entry.get('FactoryTimestamp', entry.get('RecordedTime')),
                            "ValueInMgPerDl": entry.get('ValueInMgPerDl', entry.get('Value')),
                            "TrendArrow": entry.get('TrendArrow', entry.get('trend'))
                        }
                        readings.append(reading)
            
            return readings
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error while fetching glucose data: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching glucose data: {str(e)}")

    def validate_nightscout_api(self) -> bool:
        """Validate Nightscout API connection and token."""
        try:
            url = f"{self.config['nightscout']['url']}/api/v1/status"
            headers = {
                "api-secret": self.config["nightscout"]["api_token"],
                "Accept": "application/json"
            }
            
            response = self.nightscout_session.get(url, headers=headers)
            response.raise_for_status()
            
            # Check if response is HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                # Check if HTML response contains "STATUS OK"
                return 'STATUS OK' in response.text
            
            # Try JSON response
            try:
                status = response.json()
                return 'status' in status and status['status'] == 'ok'
            except json.JSONDecodeError:
                # If JSON parsing fails but we got a successful response, consider it valid
                return response.status_code == 200
            
        except Exception as e:
            print(f"Nightscout API validation failed: {e}")
            return False

    def get_last_nightscout_entry(self) -> dict:
        """Get the most recent entry from Nightscout."""
        try:
            url = f"{self.config['nightscout']['url'].rstrip('/')}/api/v1/entries.json"  # Ensure proper URL format
            headers = {
                "api-secret": self.config["nightscout"]["api_token"],
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            params = {
                "count": 1,
                "find[type]": "sgv"  # Only get SGV entries
            }
            
            response = self.nightscout_session.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            # Debug the response
            print(f"Nightscout Response Status: {response.status_code}")
            print(f"Nightscout Response Headers: {response.headers}")
            
            try:
                entries = response.json()
                if isinstance(entries, list) and len(entries) > 0:
                    return entries[0]
                return None
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error. Response content: {response.text[:200]}...")  # Print first 200 chars
                raise
            
        except requests.exceptions.RequestException as e:
            print(f"Network error while fetching Nightscout entry: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing Nightscout response: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error while fetching Nightscout entry: {e}")
            return None

    def upload_to_nightscout(self, entries: list) -> None:
        """Upload glucose entries to Nightscout."""
        if not entries:
            print("No new glucose readings to upload")
            return
        
        # Get the last entry from Nightscout
        last_entry = self.get_last_nightscout_entry()
        last_entry_time = None
        if last_entry and 'date' in last_entry:
            last_entry_time = last_entry['date']
        
        headers = {
            "api-secret": self.config["nightscout"]["api_token"],
            "Content-Type": "application/json"
        }
        
        nightscout_entries = []
        skipped_count = 0
        
        for entry in entries:
            try:
                timestamp = datetime.strptime(entry["Timestamp"], "%m/%d/%Y %I:%M:%S %p")
                entry_time = int(timestamp.timestamp() * 1000)
                
                # Skip if this entry is older than or equal to the last Nightscout entry
                if last_entry_time and entry_time <= last_entry_time:
                    skipped_count += 1
                    continue
                    
                nightscout_entry = {
                    "type": "sgv",
                    "dateString": timestamp.isoformat() + 'Z',  # Add UTC indicator
                    "date": entry_time,
                    "sgv": entry["ValueInMgPerDl"],
                    "device": "librelink-up"
                }
                
                if "TrendArrow" in entry and entry["TrendArrow"] is not None:
                    nightscout_entry["direction"] = self.map_trend_arrow(entry["TrendArrow"])
                    
                nightscout_entries.append(nightscout_entry)
                
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping invalid entry: {e}")
                continue

        if nightscout_entries:
            # Sort entries by date to ensure chronological order
            nightscout_entries.sort(key=lambda x: x['date'])
            
            url = f"{self.config['nightscout']['url']}/api/v1/entries"
            response = self.nightscout_session.post(url, json=nightscout_entries, headers=headers)
            response.raise_for_status()
            print(f"Successfully uploaded {len(nightscout_entries)} new readings to Nightscout")
        else:
            print(f"No new readings to upload (skipped {skipped_count} duplicate entries)")

    @staticmethod
    def map_trend_arrow(arrow_value: int) -> str:
        """Map LibreLink trend arrow to Nightscout direction."""
        mapping = {
            1: "SingleDown",
            2: "FortyFiveDown",
            3: "Flat",
            4: "FortyFiveUp",
            5: "SingleUp"
        }
        return mapping.get(arrow_value, "NOT COMPUTABLE")

def main():
    # Validate required environment variables
    required_env_vars = [
        "LIBRELINK_USERNAME",
        "LIBRELINK_PASSWORD",
        "LIBRELINK_REGION",
        "NIGHTSCOUT_URL",
        "NIGHTSCOUT_API_TOKEN"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    try:
        uploader = LibreLinkUploader(credentials)
        
        # Validate Nightscout API before proceeding
        if not uploader.validate_nightscout_api():
            raise Exception("Failed to validate Nightscout API connection")
            
        uploader.authenticate()
        glucose_data = uploader.get_glucose_data()
        uploader.upload_to_nightscout(glucose_data)
        print("Sync completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()