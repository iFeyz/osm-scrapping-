import requests
import csv
from datetime import datetime

def fetch_cameras(area, output_file):
    # Overpass API endpoint
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Query to find surveillance cameras in the specified area
    overpass_query = f"""
    [out:json];
    area[name="{area}"]->.searchArea;
    (
        // All surveillance cameras except indoor ones
        node["man_made"="surveillance"]["surveillance:type"="camera"](area.searchArea);
        node["surveillance"="camera"](area.searchArea);
        node["camera:type"](area.searchArea);
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
    
    # Extract camera information
    cameras = []
    for element in data.get('elements', []):
        if element.get('type') == 'node':
            tags = element.get('tags', {})
            
            # Skip if explicitly marked as indoor
            if tags.get('surveillance:mounted') == 'indoor' or tags.get('surveillance:zone') == 'indoor':
                continue
                
            camera = {
                'city': area,
                'latitude': element.get('lat'),
                'longitude': element.get('lon'),
            }
            cameras.append(camera)
    
    return cameras

def save_to_csv(cameras, filename):
    if not cameras:
        print("No cameras found to save.")
        return
    
    # Updated CSV headers to include new fields
    headers = ['city', 'latitude', 'longitude', 
            ]
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(cameras)

def main():
    # Cities to scrape
    cities = ['Paris', 'Nantes']
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'security_cameras_{timestamp}.csv'
    
    all_cameras = []
    
    # Fetch cameras for each city
    for city in cities:
        print(f"Fetching cameras in {city}...")
        cameras = fetch_cameras(city, output_file)
        all_cameras.extend(cameras)
        print(f"Found {len(cameras)} cameras in {city}")
    
    # Save all results to CSV
    save_to_csv(all_cameras, output_file)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main() 