@ECHO OFF

python Converer(binaryToB64).py
python AssemblyMatch.py

del Assembly-CSharp.txt.b64
del ModdedAssembly-CSharp.txt.b64