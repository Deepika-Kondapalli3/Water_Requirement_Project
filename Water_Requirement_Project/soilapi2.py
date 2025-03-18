import requests
import json
from datetime import datetime, timedelta

class SoilDataFetcher:
    def __init__(self):
        self.nasa_power_base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        self.soilgrids_base_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        
    def get_nasa_power_data(self, lat, lon):
        """
        Fetch soil moisture and evaporation data from NASA POWER API
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        params = {
            'parameters': 'SOIL_M,EVLAND',
            'community': 'AG',
            'longitude': lon,
            'latitude': lat,
            'start': start_date.strftime('%Y%m%d'),
            'end': end_date.strftime('%Y%m%d'),
            'format': 'JSON'
        }
        
        try:
            response = requests.get(self.nasa_power_base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'properties' not in data:
                print("No data available from NASA POWER API")
                return None
                
            properties = data['properties']
            latest_date = max(properties['parameter'].get('SOIL_M', {}).keys())
            
            return {
                'soil_moisture': properties['parameter']['SOIL_M'][latest_date],
                'evaporation_rate': properties['parameter']['EVLAND'][latest_date]
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching NASA POWER data: {e}")
            return None

    def get_soil_properties(self, lat, lon):
        """
        Fetch comprehensive soil properties from SoilGrids
        """
        try:
            url = f"{self.soilgrids_base_url}?lon={lon}&lat={lat}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            #print(data)
            
            soil_data = {}
            property_details = {
                'bdod': {
                    'name': 'bulk_density',
                    'unit': 'kg/dm³'
                },
                'cec': {
                    'name': 'cation_exchange_capacity',
                    'unit': 'cmol(c)/kg'
                },
                'clay': {
                    'name': 'clay_content',
                    'unit': '%'
                },
                'sand': {
                    'name': 'sand_content',
                    'unit': '%'
                },
                'silt': {
                    'name': 'silt_content',
                    'unit': '%'
                },
                'nitrogen': {
                    'name': 'nitrogen_content',
                    'unit': 'g/kg'
                },
                'phh2o': {
                    'name': 'ph',
                    'unit': 'pH'
                },
                'soc': {
                    'name': 'soil_organic_carbon',
                    'unit': 'g/kg'
                },
                'wv0010': {
                    'name': 'water_content_0_10kpa',
                    'unit': 'cm³/cm³'
                },
                'wv0033': {
                    'name': 'water_content_33kpa',
                    'unit': 'cm³/cm³'
                },
                'wv1500': {
                    'name': 'water_content_1500kpa',
                    'unit': 'cm³/cm³'
                }
            }
            
            for layer in data['properties']['layers']:
                property_name = layer['name']
                if property_name in property_details:
                    # Get values for different depths
                    depths_data = {}
                    for depth in layer['depths']:
                        depth_label = depth['label']
                        mean_value = depth['values']['mean']
                        
                        if mean_value is not None:
                            # Convert units based on d_factor
                            d_factor = layer['unit_measure']['d_factor']
                            mean_value = mean_value / d_factor
                            depths_data[depth_label] = {
                                'value': mean_value,
                                'unit': property_details[property_name]['unit']
                            }
                    
                    if depths_data:
                        soil_data[property_details[property_name]['name']] = depths_data
            
            return soil_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching soil properties: {e}")
            return None

    def get_all_soil_data(self, lat, lon):
        """
        Get combined soil data from both APIs
        """
        result = {
            'location': {
                'latitude': lat,
                'longitude': lon,
                'timestamp': datetime.now().isoformat()
            }
        }

        try:
        
            # Get real-time moisture and evaporation from NASA
            nasa_data = self.get_nasa_power_data(lat, lon)
            if nasa_data:
                result['nasa_power_data'] = nasa_data
                
            # Get comprehensive soil properties from SoilGrids
            soil_props = self.get_soil_properties(lat, lon)
            if soil_props:
                result['soil_properties'] = soil_props
                
            return result
        except:
            return  None 

def main():
    # Example coordinates (New York City)
    lat, lon = -9, -72 #  40.7128, -74.0060
    
    fetcher = SoilDataFetcher()
    #soil_data = fetcher.get_all_soil_data(lat, lon)
    #print(json.dumps(soil_data, indent=2))

    soil_ph = fetcher.get_soil_properties(lat, lon)
    print('soil data starts here ...',json.dumps(soil_ph))

if __name__ == "__main__":
    main()