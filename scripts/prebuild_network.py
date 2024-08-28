import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from service_accessibility.services.build_extended_network import build_and_save

if __name__ == "__main__":
    build_and_save()
