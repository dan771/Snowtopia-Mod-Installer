import binascii
import base64

NewAssembly =open("NewAssembly.txt.b64", "r").read()
NewAssemblyDll =open("Assembly-CSharpM.dll", "wb")

NewAssembly = base64.b64decode(NewAssembly).hex()

binary_string = binascii.unhexlify(NewAssembly)

NewAssemblyDll.write(binary_string)
