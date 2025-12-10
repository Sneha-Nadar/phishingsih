# extract_stego.py
from PIL import Image
import numpy as np
import sys

def extract_lsb(path):
    img = Image.open(path).convert("RGB")
    data = np.array(img)

    bits = []
    for channel in range(3):  # R,G,B
        bits.extend((data[:,:,channel] & 1).flatten())

    # convert bits → bytes
    bytes_out = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        value = 0
        for bit in byte:
            value = (value << 1) | bit
        bytes_out.append(value)

    # convert bytes to string (stop at null)
    message = ""
    for b in bytes_out:
        if b == 0:
            break
        if 32 <= b <= 126:  # printable ASCII
            message += chr(b)
        else:
            message += "?"

    return message


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_stego.py image.png")
        sys.exit(1)

    result = extract_lsb(sys.argv[1])
    print("\nEXTRACTED (LSB):\n")
    print(result)
