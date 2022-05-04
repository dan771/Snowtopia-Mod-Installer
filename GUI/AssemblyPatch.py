import base64
import imp
from locale import currency
import diff_match_patch as dmp_module
import os

def Patch(changeLogDir, NewAssembly):
    dmp = dmp_module.diff_match_patch()

    Assembly = open("Assembly-CSharp.txt.b64", "r").read() #original
    NAssembly = open(NewAssembly, "w") #modded(to make)

    changeLog = open(changeLogDir, 'r').read()

    patches = dmp.patch_fromText(changeLog) #gets pacthes
    Final = dmp.patch_apply(patches, Assembly)[0] #converts Assembly into modded(only need first in list output)

    NAssembly.write(Final)
    NAssembly.close()