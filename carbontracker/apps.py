import sqlite3
import sys
from pathlib import Path
from django.apps import AppConfig
from django.conf import settings


class CarbontrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'carbontracker'

    def ready(self):
        """Initialize app - import vehicle data on startup"""
        print("\n" + "="*70)
        print("🚀 CarbontrackerConfig.ready() called")
        print("="*70)
        
        try:
            from carbontracker.models import Car
            from django.db import connection
            
            # Check if database is accessible
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print("✅ Database connection OK")
            
            # Check if vehicles already exist
            existing_count = Car.objects.filter(is_user_vehicle=False).count()
            print(f"📊 Existing vehicles in DB: {existing_count}")
            
            if existing_count > 0:
                print("✅ Vehicles already imported, skipping")
                return
            
            # Try to import
            print("🔄 Starting vehicle import...")
            self.import_vehicles()
            
        except Exception as e:
            print(f"⚠️  Error during app initialization: {e}")
            import traceback
            traceback.print_exc()
    
    def import_vehicles(self):
        """Import vehicle data from SQLite"""
        from carbontracker.models import Car
        
        db_path = Path(settings.BASE_DIR) / 'data' / 'megaDataPack.sqlite'
        print(f"📂 Looking for data at: {db_path}")
        print(f"   Exists: {db_path.exists()}")
        
        if not db_path.exists():
            print(f"❌ Data file not found!")
            return
        
        try:
            print("📖 Reading SQLite database...")
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM VehicleData')
            total = cursor.fetchone()[0]
            print(f"   Found {total} rows in VehicleData")
            
            # Get actual data
            cursor.execute('SELECT make, model, year, city08, highway08, drive, displ, trany, VClass, fuelType FROM VehicleData')
            rows = cursor.fetchall()
            print(f"   Fetched {len(rows)} vehicle records")
            
            if not rows:
                print("❌ No rows returned!")
                return
            
            # Create Car objects
            print(f"🏭 Creating Car objects...")
            cars_to_create = []
            
            for i, row in enumerate(rows):
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
                    is_user_vehicle=False,
                )
                cars_to_create.append(car)
            
            print(f"   Prepared {len(cars_to_create)} Car objects")
            
            # Insert into database
            print(f"💾 Inserting into database...")
            Car.objects.bulk_create(cars_to_create, batch_size=500)
            
            # Verify
            count = Car.objects.filter(is_user_vehicle=False).count()
            print(f"✅ SUCCESS! Imported {count} vehicles to database")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            import traceback
            traceback.print_exc()
