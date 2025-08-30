import sys
import os

def print_section(title):
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)

def main():
    print_section("Python Environment Verification")
    
    # Basic Python info
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Check if we can write to the current directory
    try:
        test_file = "test_write.txt"
        with open(test_file, 'w') as f:
            f.write("Test successful!")
        os.remove(test_file)
        print("✅ Can write to current directory")
    except Exception as e:
        print(f"❌ Cannot write to current directory: {e}")
    
    # Check OpenCV installation
    print_section("OpenCV Check")
    try:
        import cv2
        print(f"OpenCV Version: {cv2.__version__}")
        print(f"OpenCV Path: {cv2.__file__}")
        
        # Check if we can load the cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        print(f"\nLooking for cascade at: {cascade_path}")
        
        if not os.path.exists(cascade_path):
            print("❌ Cascade file not found!")
            print("This usually means OpenCV was not installed with the haarcascades.")
            print("Try reinstalling with: pip uninstall opencv-python opencv-contrib-python")
            print("Then: pip install opencv-contrib-python")
        else:
            print("✅ Cascade file found")
            
            # Try to load the cascade
            try:
                face_cascade = cv2.CascadeClassifier(cascade_path)
                if face_cascade.empty():
                    print("❌ Could not load cascade classifier")
                else:
                    print("✅ Successfully loaded cascade classifier")
            except Exception as e:
                print(f"❌ Error loading cascade: {e}")
                
    except ImportError:
        print("❌ OpenCV is not installed")
        print("Install it with: pip install opencv-contrib-python")
    except Exception as e:
        print(f"❌ Error checking OpenCV: {e}")
    
    # Check Django installation
    print_section("Django Check")
    try:
        import django
        print(f"Django Version: {django.get_version()}")
        print(f"Django Path: {django.__file__}")
    except ImportError:
        print("❌ Django is not installed")
        print("Install it with: pip install django")
    except Exception as e:
        print(f"❌ Error checking Django: {e}")
    
    # Check database file
    print_section("Database Check")
    db_path = os.path.join(os.getcwd(), 'db.sqlite3')
    print(f"Database path: {db_path}")
    
    if os.path.exists(db_path):
        print(f"✅ Database file exists ({os.path.getsize(db_path)} bytes)")
    else:
        print("❌ Database file does not exist!")
        print("Run migrations with: python manage.py migrate")
    
    print_section("Test Complete")
    print("\nIf you see any ❌ errors above, please address them before continuing.")

if __name__ == "__main__":
    main()
