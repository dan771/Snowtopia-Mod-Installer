@ECHO OFF
python Converter(binaryToB64).py 
python AssemblyPatch.py 
python Converter(b64ToBinary).py

del Assembly-CSharp.txt.b64
del NewAssembly.txt.b64