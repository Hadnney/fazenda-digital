import cv2
import numpy as np
from pyzbar.pyzbar import decode

# Create a simple dummy image (black)
img = np.zeros((100, 100, 3), dtype=np.uint8)

try:
    print("Testando pyzbar decode...")
    res = decode(img)
    print("Decode executado com sucesso! Resultado:", res)
except Exception as e:
    print("Erro ao executar decode:", Exception(e))
