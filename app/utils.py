import uuid
import os
import treepoem  # not segno!

def generate_uid():
    return str(uuid.uuid4())

def generate_aztec_code(data):
    output_folder = os.path.join('static', 'aztec_codes')
    os.makedirs(output_folder, exist_ok=True)

    filename = f"{data}_aztec.png"
    filepath = os.path.join(output_folder, filename)

    # treepoem generates Aztec code
    image = treepoem.generate_barcode(
        barcode_type='azteccode',
        data=data
    )

    image.convert("1").save(filepath)

    return filepath
