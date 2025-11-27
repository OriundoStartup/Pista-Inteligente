import os
import sys

if __name__ == "__main__":
    # Este script sirve como punto de entrada alternativo o launcher
    # Ejecuta la aplicación Streamlit en el puerto estándar de HF Spaces
    os.system("streamlit run app_frontend.py --server.port 7860 --server.address 0.0.0.0")
