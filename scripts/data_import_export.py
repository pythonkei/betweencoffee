import csv
import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coffee_delivery.settings')
django.setup()

from coffee.models import Coffee

def export_coffee_data(output_file='coffee_data.csv'):
    """Export coffee data to CSV file"""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'name', 'description', 'short_description', 'price', 
            'origin', 'roast_level', 'flavor_profile', 'image_path'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for coffee in Coffee.objects.all():
            writer.writerow({
                'name': coffee.name,
                'description': coffee.description,
                'short_description': coffee.short_description,
                'price': str(coffee.price),
                'origin': coffee.origin,
                'roast_level': coffee.roast_level,
                'flavor_profile': coffee.flavor_profile,
                'image_path': coffee.image.path if coffee.image else ''
            })

def import_coffee_data(input_file='coffee_data.csv', image_dir='coffee_images'):
    """Import coffee data from CSV file"""
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Create coffee instance
            coffee = Coffee(
                name=row['name'],
                description=row['description'],
                short_description=row['short_description'],
                price=row['price'],
                origin=row['origin'],
                roast_level=row['roast_level'],
                flavor_profile=row['flavor_profile']
            )
            
            # Handle image import
            image_path = row['image_path']
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    coffee.image.save(
                        os.path.basename(image_path),
                        File(f)
                    )
            
            coffee.save()

def clean_data(input_file='coffee_data.csv'):
    """Clean and validate coffee data"""
    cleaned_data = []
    
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Clean and validate each field
            cleaned_row = {
                'name': row['name'].strip(),
                'description': row['description'].strip(),
                'short_description': row['short_description'].strip(),
                'price': row['price'].strip(),
                'origin': row['origin'].strip(),
                'roast_level': row['roast_level'].strip().upper()[0],  # Only first letter
                'flavor_profile': row['flavor_profile'].strip(),
                'image_path': row['image_path'].strip()
            }
            
            # Validate roast level
            if cleaned_row['roast_level'] not in ['L', 'M', 'D']:
                cleaned_row['roast_level'] = 'M'  # Default to Medium
                
            # Validate price
            try:
                float(cleaned_row['price'])
            except ValueError:
                cleaned_row['price'] = '0.00'
                
            cleaned_data.append(cleaned_row)
    
    # Write cleaned data back to file
    with open(input_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'name', 'description', 'short_description', 'price', 
            'origin', 'roast_level', 'flavor_profile', 'image_path'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(cleaned_data)

if __name__ == '__main__':
    # Clean and import sample data
    clean_data('scripts/sample_coffee_data.csv')
    import_coffee_data('scripts/sample_coffee_data.csv')
