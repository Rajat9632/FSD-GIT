import sqlite3
from pathlib import Path
from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate


class CarbontrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'carbontracker'

    def ready(self):
        """Initialize app - import vehicle data after migrations"""
        # Connect to post_migrate signal to import data after all migrations
        post_migrate.connect(self.import_vehicle_data_on_migrate, sender=self)

    @staticmethod
    def import_vehicle_data_on_migrate(sender, **kwargs):
        """Import vehicle data after migrations complete"""
        from carbontracker.models import Car
        
        # Skip if vehicles already exist
        if Car.objects.filter(is_user_vehicle=False).exists():
            print("✅ Vehicles already imported, skipping import")
            return
        
        print("\n🚗 Importing vehicle data...")
        
        db_path = Path(settings.BASE_DIR) / 'data' / 'megaDataPack.sqlite'
        
        if not db_path.exists():
            print(f"❌ Vehicle data file not found at {db_path}")
            return
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute('SELECT make, model, year, city08, highway08, drive, displ, trany, VClass, fuelType FROM VehicleData')
            rows = cursor.fetchall()
            print(f"Found {len(rows)} vehicles in SQLite")
            
            cars_to_create = []
            for row in rows:
                make, model, year, city08, highway08, drive, displ, trany, vclass, fuelType = row
                
                if fuelType == "Electricity fuel":
                    kg_per_gallon = 0.0
                elif fuelType == "Diesel fuel":
                    kg_per_gallon = 10.16
                else:
                    kg_per_gallon = 8.89
                
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
                    is_user_vehicle=False,  # CRITICAL
                )
                cars_to_create.append(car)
            
            print(f"Creating {len(cars_to_create)} car records in database...")
            Car.objects.bulk_create(cars_to_create, batch_size=500)
            print(f"✅ Successfully imported {len(cars_to_create)} vehicles!")
            
            conn.close()
        except Exception as e:
            print(f"❌ Failed to import vehicles: {e}")
            import traceback
            traceback.print_exc()
