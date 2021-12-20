import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import os
import zipfile

import Validator
import Converter_b64ToBinary as B64toB
import AssemblyPatch
import Converter_binaryToB64 as BtoB64

LARGEFONT =("Verdana", 15)
NORMALFONT = ("Arial", 10)
SMALLFONT = ("Arial", 8)

filename = False
BasePath = False
AssemblyPath = False
ManagedPath = False
ChangeLog = 'ChangeLog.txt'
ModDataPath = 'ModData.zip'

class tkinterApp(tk.Tk):
        global filename
        # __init__ function for class tkinterApp
        def __init__(self, *args, **kwargs):

                # __init__ function for class Tk
                tk.Tk.__init__(self, *args, **kwargs)
                
                # creating a container
                container = tk.Frame(self)
                container.pack(side = "top", fill = "both", expand = False)

                self.resizable(False, False)
                
                # initializing frames to an empty array
                self.frames = {}

                # iterating through a tuple consisting
                # of the different page layouts
                for F in (StartPage, Page1, Page2, Page3, FinalPage):

                        frame = F(container, self)

                        # initializing frame of that object from
                        # startpage, page1, page2 respectively with
                        # for loop
                        self.frames[F] = frame

                        frame.grid(row = 0, column = 0, sticky ="nsew")

                self.show_frame(StartPage)

        # to display the current frame passed as
        # parameter
        def show_frame(self, cont):
                frame = self.frames[cont]
                frame.tkraise()

class StartPage(tk.Frame):
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)
                
                #heading
                label = ttk.Label(self, text ="Startpage", font = LARGEFONT)
                label.grid(row = 0, column = 0, padx = 10, pady = 15)

                #paragraph
                paragraph = ttk.Label(self, text="Welocome to the Snowtopia Modding installer.", font = NORMALFONT)
                paragraph.grid(row = 1, column = 0, pady = 15, padx = 10)

                #Next button
                button2 = ttk.Button(self, text ="Next Page",
                command = lambda : controller.show_frame(Page1))
                
                button2.grid(row = 2, column = 1, padx = 10, pady = 20)

class Page1(tk.Frame):
        global filename, ModDataToggle
        def __init__(self, parent, controller):
                
                tk.Frame.__init__(self, parent)

                #heading
                label = ttk.Label(self, text ="Enter Files", font = LARGEFONT)
                label.grid(row = 0, column = 0, padx = 90, pady = 10)

                #Entry Point text
                EPT = ttk.Label(self, text ="Input Snowtopia.exe here: ", font = NORMALFONT)
                EPT.grid(row = 1, column = 0, padx = 5, pady = 5)

                #Entry Point
                Browse = ttk.Button(self, text = "Browse A File",
                command = self.fileDialog)
                Browse.grid(column = 0, row = 2, padx = 5, pady = 2)

                global PathInput
                PathInput = tk.Text(self, font=SMALLFONT, width = 50, height = 1)
                PathInput.grid(column = 0, row = 3)
                
                #Next button
                global Page1Next
                Page1Next = ttk.Button(self, text ="Next Page",
                                                        command = lambda : controller.show_frame(Page2))

                Page1Next["state"] = "disabled"
                Page1Next.grid(row = 5, column = 1, padx = 10, pady = 10)

        def fileDialog(self):
                global filename, BasePath, AssemblyPath

                PathLabel = self.grid_slaves(column = 1, row = 2)
                for i in PathLabel:
                        i.destroy()

                PathInput.delete('1.0', 'end')
                
                filename = filedialog.askopenfilename(initialdir =  "/", title = "Select A File", filetype = (("Snowtopia File","*.exe"),("all files","*.*")) )

                if filename[-13:] == 'Snowtopia.exe':
                        
                        BasePath = filename[:-13]
                        AssemblyPath = BasePath+'Snowtopia_Data/Managed/Assembly-CSharp.dll'

                        if not os.path.exists(AssemblyPath):
                                PathLabel = ttk.Label(self, font = NORMALFONT, text = 'invalid dir(2)')
                                PathLabel.grid(column = 1, row = 2)
                                Page1Next["state"] = "disabled"

                        else:
                                PathLabel = ttk.Label(self, font = NORMALFONT, text = 'valid dir')
                                PathLabel.grid(column = 1, row = 2)

                                PathLabel.forget()
                                
                                PathInput.insert('end', filename)

                                Page1Next["state"] = "enabled"

                else:
                        PathLabel = ttk.Label(self, font = NORMALFONT, text = 'invalid dir(1)')
                        PathLabel.grid(column = 1, row = 2)
                        Page1Next["state"] = "disabled"

class Page2(tk.Frame):
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)

                #heading
                label = ttk.Label(self, text ="Validate", font = LARGEFONT)
                label.grid(row = 0, column = 0, padx = 110, pady = 10)

                WarningLabel = ttk.Label(self, text ="This may take a few moments", font = NORMALFONT)
                WarningLabel.grid(row = 1, column = 0, padx = 5)
                
                #validate button
                ValidateButton = ttk.Button(self, text ="Validate",
                                                        command = self.Validate)

                ValidateButton.grid(row = 2, column = 0, padx = 10)
                
                #Next button
                global Page2Next
                Page2Next = ttk.Button(self, text ="Next Page",
                                                        command = lambda : controller.show_frame(Page3))

                Page2Next['state'] = 'disabled'
                Page2Next.grid(row = 4, column = 1, padx = 10, pady = 10)

        def Validate(self):
                ValidatingLabel = ttk.Label(self, text ="Validating...", font = NORMALFONT)
                ValidatingLabel.grid(row = 2, column = 1)
                
                result = Validator.Validate(AssemblyPath)

                if result == 3891662:
                        ResultLabel = ttk.Label(self, text ="Validated Sucsessfully!", font = NORMALFONT)
                        Page2Next['state'] = 'enabled'

                else:
                        ResultLabel = ttk.Label(self, text ="got "+str(result)+ ", expected 3891662", font = NORMALFONT)

                ResultLabel.grid(row = 3, column = 0, pady = 5)

class Page3(tk.Frame):
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)
                label = ttk.Label(self, text ="Install", font = LARGEFONT)
                label.grid(row = 0, column = 0, padx = 120, pady = 10)

                WarningLabel = ttk.Label(self, text ="This may take a few moments", font = NORMALFONT)
                WarningLabel.grid(row = 1, column = 0, padx = 5)

                #Install button
                InstallButton = ttk.Button(self, text ="Install",
                                                        command = self.Install)

                InstallButton.grid(row = 2, column = 0, padx = 10)

                #next
                button1 = ttk.Button(self, text ="Next Page",
                                                        command = lambda : controller.show_frame(FinalPage))

                button1.grid(row = 4, column = 1, padx = 10, pady = 10)

        def Install(self):
                ValidatingLabel = ttk.Label(self, text ="Installing...", font = NORMALFONT)
                ValidatingLabel.grid(row = 2, column = 1)

                BtoB64.Convert(AssemblyPath)
                AssemblyPatch.Patch()
                B64toB.Convert(AssemblyPath)

                if os.path.exists(ModDataPath):                
                        with zipfile.ZipFile(ModDataPath, 'r') as zip_ref: 
                                zip_ref.extractall(BasePath+"ModData")
                
                ResultLabel = ttk.Label(self, text ="Installed Sucsessfully!", font = NORMALFONT)
                ResultLabel.grid(row = 3, column = 0, pady = 5)


class FinalPage(tk.Frame):
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)
                label = ttk.Label(self, text ="Thanks for Installing", font = LARGEFONT)
                label.grid(row = 0, column = 0, padx = 10, pady = 10)

                # button to show frame 2 with text
                # layout2
                button1 = ttk.Button(self, text ="Exit",
                                                        command = quit)
        
                # putting the button in its place by
                # using grid
                button1.grid(row = 2, column = 2, padx = 10, pady = 10)

# Driver Code
app = tkinterApp()
app.mainloop()
