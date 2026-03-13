import sqlite3
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from carbontracker.models import Car

class Command(BaseCommand):
    help = 'Import vehicle data from megaDataPack.sqlite into Car model'

    def handle(self, *args, **options):
        # Use BASE_DIR from settings for proper path resolution
        db_path = Path(settings.BASE_DIR) / 'data' / 'megaDataPack.sqlite'
        
        self.stdout.write(f"Looking for vehicle data at: {db_path}")
        
        if not db_path.exists():
            self.stdout.write(self.style.ERROR(f'ERROR: Vehicle data file not found at {db_path}'))
            return
        
        try:
            # Read from SQLite
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute('SELECT make, model, year, city08, highway08, drive, displ, trany, VClass, fuelType FROM VehicleData')
            rows = cursor.fetchall()
            self.stdout.write(f"Found {len(rows)} vehicles in SQLite database")
            
            # Try to get existing cars (but don't fail if database is down)
            existing_cars = set()
            try:
                existing_cars = set(Car.objects.values_list('make', 'model', 'year'))
                self.stdout.write(f"Found {len(existing_cars)} existing vehicles in Django database")
            except Exception as db_error:
                self.stdout.write(f"⚠️  Could not query Django database: {db_error}")
                self.stdout.write("⚠️  Will attempt to import all vehicles anyway")
            
            cars_to_create = []
            
            for row in rows:
                make, model, year, city08, highway08, drive, displ, trany, vclass, fuelType = row
                # Calculate kg_per_gallon based on fuelType
                if fuelType == "Electricity fuel":
                    kg_per_gallon = 0.0
                elif fuelType == "Diesel fuel":
                    kg_per_gallon = 10.16
                else:
                    kg_per_gallon = 8.89
                
                # Only create if not already in database (or if we couldn't check)
                if (make, model, str(year)) not in existing_cars:
                    car = Car(
                        make=make,
                        model=model,
                        year=str(year),
                        city_km_per_gallon=city08,
                        highway_km_per_gallon=highway08,
                        drive=drive,
                        disp=displ,
                        transmission=trany,
                        v_class=vclass,
                        fuel_type=fuelType,
                        kg_per_gallon=kg_per_gallon,
                        is_user_vehicle=False  # CRITICAL: Mark as available for users
                    )
                    cars_to_create.append(car)
            
            self.stdout.write(f"Prepared {len(cars_to_create)} vehicles for import")
            
            if cars_to_create:
                Car.objects.bulk_create(cars_to_create, batch_size=1000)
                self.stdout.write(self.style.SUCCESS(f'✅ Successfully imported {len(cars_to_create)} new vehicles'))
            else:
                self.stdout.write(self.style.WARNING(f'ℹ️  No new vehicles to import (all vehicles already exist)'))
            
            conn.close()
            
        except sqlite3.Error as sqlite_error:
            self.stdout.write(self.style.ERROR(f'❌ SQLite error: {str(sqlite_error)}'))
            raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to import vehicles: {str(e)}'))
            raise
