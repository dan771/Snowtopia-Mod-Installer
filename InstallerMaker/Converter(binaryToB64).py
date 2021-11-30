import binascii
import codecs

Converted = open("Assembly-CSharp.txt.b64", "w")
ModdedAssembly = open("ModdedAssembly-CSharp.txt.b64", "w")

# Open in binary mode (so you don't read two byte line endings on Windows as one byte)
# and use with statement (always do this to avoid leaked file descriptors, unflushed files)
with open('Assembly-CSharp.dll', 'rb') as f:
    # Slurp the whole file and efficiently convert it to hex all at once
    hexdata = binascii.hexlify(f.read())
    hex = hexdata
    b64data = codecs.encode(codecs.decode(hex, 'hex'), 'base64').decode()
    
    Converted.write(b64data)

with open('ModdedAssembly-CSharp.dll', 'rb') as f:
    # Slurp the whole file and efficiently convert it to hex all at once
    hexdata = binascii.hexlify(f.read())
    hex = hexdata
    b64data = codecs.encode(codecs.decode(hex, 'hex'), 'base64').decode()
    
    ModdedAssembly.write(b64data)
