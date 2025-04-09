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

    # ✅ Correct way to generate Aztec code using latest AND older segno
    aztec = segno.make(data)  # no keyword arguments
    aztec.save(filepath, kind='aztec', scale=5)  # ✅ Specify kind here

    return filepath
