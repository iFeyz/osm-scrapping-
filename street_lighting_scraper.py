import requests
import csv
from datetime import datetime

def fetch_lit_streets(area, output_file):
    # Overpass API endpoint
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Query to find lit streets in the specified area
    overpass_query = f"""
    [out:json];
    area[name="{area}"]->.searchArea;
    (
        way["highway"]["lit"="yes"](area.searchArea);
        way["highway"]["lit"="24/7"](area.searchArea);
        way["highway"]["lighting"="yes"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    
    # Make the request
    response = requests.post(overpass_url, data=overpass_query)
    
    if response.status_code != 200:
        print(f"Error fetching data for {area}: {response.status_code}")
        return []
    
    # Parse the response
    data = response.json()
    
    # Extract street lighting information
    lit_streets = []
    nodes = {node['id']: (node['lat'], node['lon']) 
             for node in data.get('elements', []) 
             if node['type'] == 'node'}
    
    for element in data.get('elements', []):
        if element.get('type') == 'way':
            tags = element.get('tags', {})
            if 'highway' in tags and ('lit' in tags or 'lighting' in tags):
                # Get coordinates for the street (first and last node)
                nodes_refs = element.get('nodes', [])
                if nodes_refs:
                    start_coords = nodes.get(nodes_refs[0], (None, None))
                    end_coords = nodes.get(nodes_refs[-1], (None, None))
                    
                    street = {
                        'city': area,
                        'street_name': tags.get('name', 'unknown'),
                        'highway_type': tags.get('highway', 'unknown'),
                        'lighting_status': tags.get('lit', tags.get('lighting', 'unknown')),
                        'start_lat': start_coords[0],
                        'start_lon': start_coords[1],
                        'end_lat': end_coords[0],
                        'end_lon': end_coords[1],
                        'length': len(nodes_refs)  # approximate length by number of nodes
                    }
                    lit_streets.append(street)
    
    return lit_streets

def save_to_csv(streets, filename):
    if not streets:
        print("No lit streets found to save.")
        return
    
    # Define CSV headers
    headers = ['city', 'street_name', 'highway_type', 'lighting_status', 
              'start_lat', 'start_lon', 'end_lat', 'end_lon', 'length']
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(streets)

def main():
    # Cities to scrape
    cities = ['Paris', 'Nantes']
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'street_lighting_{timestamp}.csv'
    
    all_streets = []
    
    # Fetch lit streets for each city
    for city in cities:
        print(f"Fetching lit streets in {city}...")
        streets = fetch_lit_streets(city, output_file)
        all_streets.extend(streets)
        print(f"Found {len(streets)} lit streets in {city}")
    
    # Save all results to CSV
    save_to_csv(all_streets, output_file)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main() 