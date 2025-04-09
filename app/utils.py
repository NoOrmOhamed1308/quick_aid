# utils.py
import uuid
import segno
import os

def generate_uid():
    return str(uuid.uuid4())

def generate_aztec_code(data):
    output_folder = os.path.join('static', 'aztec_codes')
    os.makedirs(output_folder, exist_ok=True)
    
    filename = f"{data}_aztec.png"
    filepath = os.path.join(output_folder, filename)

    aztec = segno.make(data, micro=False, symbol='aztec')
    aztec.save(filepath, scale=5)

    return filepath