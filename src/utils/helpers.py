import base64
import os

def get_base64_image(image_path):
    """Convierte una imagen a base64 para embeber en HTML"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    except:
        pass
    return ""

def load_css(css_file_path):
    """Lee un archivo CSS y retorna su contenido como string"""
    try:
        with open(css_file_path, "r") as f:
            return f.read()
    except Exception as e:
        return ""
