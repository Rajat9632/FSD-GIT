from django.core.management.base import BaseCommand
from django.conf import settings
from carbontracker.models import Car

class Command(BaseCommand):
    help = 'Diagnostic: Check vehicle database status'

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write("🔍 VEHICLE DATABASE DIAGNOSTIC")
        self.stdout.write("=" * 70)
        
        try:
            # Database info
            db_config = settings.DATABASES['default']
            self.stdout.write(f"\n📊 Database: {db_config['ENGINE']}")
            self.stdout.write(f"   Host: {db_config['HOST']}")
            self.stdout.write(f"   Name: {db_config['NAME']}")
            
            # Total vehicles
            total = Car.objects.count()
            self.stdout.write(f"\n📈 Total vehicles in database: {total}")
            
            # Available vehicles (is_user_vehicle=False)
            available = Car.objects.filter(is_user_vehicle=False).count()
            self.stdout.write(f"✅ Available for users (is_user_vehicle=False): {available}")
            
            # User vehicles (is_user_vehicle=True)
            user_vehicles = Car.objects.filter(is_user_vehicle=True).count()
            self.stdout.write(f"👤 User-added vehicles (is_user_vehicle=True): {user_vehicles}")
            
            # Sample some vehicles
            if available > 0:
                self.stdout.write(f"\n🚗 Sample vehicles (first 5):")
                samples = Car.objects.filter(is_user_vehicle=False)[:5]
                for i, car in enumerate(samples, 1):
                    self.stdout.write(f"   {i}. {car.make} {car.model} ({car.year}) - Fuel: {car.fuel_type}")
            else:
                self.stdout.write("\n❌ NO VEHICLES FOUND! Database is empty.")
                self.stdout.write("   This means:")
                self.stdout.write("   - Import command never ran, OR")
                self.stdout.write("   - Import failed silently, OR")
                self.stdout.write("   - is_user_vehicle flag wasn't set correctly")
            
            self.stdout.write("\n" + "=" * 70)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error checking database: {e}"))
            import traceback
            traceback.print_exc()
