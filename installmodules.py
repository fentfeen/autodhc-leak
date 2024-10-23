import subprocess

required_modules = [
    "interactions.py",
    "requests",
    "beautifulsoup4",
    "Flask",
    "Pillow",
    "pycryptodome"
]

def import_or_install(module_name):
    try:
        __import__(module_name)
    except ImportError:
        print(f"{module_name} is not installed. Installing now...")
        subprocess.check_call(["pip", "install", module_name])

for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        print(f"Checking if {module} is already installed...")
        import_or_install(module)