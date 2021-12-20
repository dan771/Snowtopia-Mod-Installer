import base64
import diff_match_patch as dmp_module

def Patch():
    dmp = dmp_module.diff_match_patch()

    Assembly =open("Assembly-CSharp.txt.b64", "r").read() #original
    NAssembly =open("NewAssembly.txt.b64", "w") #modded(to make)

    changeLog =open("changeLog.txt", "r").read() #where all pacthes are store

    patches = dmp.patch_fromText(changeLog) #gets pacthes
    Final = dmp.patch_apply(patches, Assembly)[0] #converts Assembly into modded(only need first in list output)

    NAssembly.write(Final)
