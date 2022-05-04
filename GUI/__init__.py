import tkinter as tk
from tkinter import DISABLED, ttk
from tkinter import filedialog
from tkinter import messagebox

import shutil

import sys
import os
import zipfile

from distutils import command
from distutils.command import install

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
current = os.path.dirname(os.path.abspath(__file__))
ChangeLogs = os.listdir(f'{current}/ChangeLogs/')
CurrentChangeLog = False
SelectedChangeLog = False
ModDataZip = 'ModData.zip'
maps = os.listdir(f'{current}/maps/')
SelectedMaps = []

#custom logging
class Logger(object):
        def __init__(self):
                self.terminal = sys.stdout
                self.log = open("logfile.log", "w", encoding="utf8")

        def write(self, message):
                self.terminal.write(message)
                self.log.write(message)  

        def flush(self):
                pass

        def close(self):
                self.log.close()

sys.stdout = Logger()

class tkinterApp(tk.Tk):
        global filename
        # __init__ function for class tkinterApp
        def __init__(self, *args, **kwargs):

                # __init__ function for class Tk
                tk.Tk.__init__(self, *args, **kwargs)
                
                # creating a container
                container = tk.Frame(self)
                container.pack(side = "top", fill = "both", expand = False)
                
                self.geometry('450x325+700+200')
                self.title('Snowtopia Mod Installer')

                self.resizable(False, False)
                
                # initializing frames to an empty array
                self.frames = {}

                # iterating through a tuple consisting
                # of the different page layouts
                for F in (StartPage, EnterFile, Configure, Validate, InstallPage, FinalPage):
                        frame = F(container, self)

                        # initializing frame of that object from
                        # pages respectively with
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

                #blank space (padding + filling)
                fill1 = ttk.Label(self, text='')
                fill1.grid(row = 0, column = 0, pady=25, padx = 220)

                #heading
                label = ttk.Label(self, text ="Startpage", font = LARGEFONT)
                label.grid(row = 1, column = 0, padx = 15, pady = 15)

                #paragraph
                paragraph = ttk.Label(self, text="Welcome to the Snowtopia Mod installer!", font = NORMALFONT)
                paragraph.grid(row = 2, column = 0, pady = 15, padx = 10)
                
                #blank space (padding)
                fill2 = ttk.Label(self, text='')
                fill2.grid(row = 3, column = 0, pady=40)

                #Next button
                button2 = ttk.Button(self, text ="Next Page",
                command = lambda : controller.show_frame(EnterFile))
                
                button2.grid(row = 4, column = 0, padx = 10, pady = 10, sticky = tk.E)

class EnterFile(tk.Frame):
        global filename, ModDataToggle
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)

                #blank space (padding + filling)
                fill1 = ttk.Label(self, text='')
                fill1.grid(row = 0, column = 0, pady=15, padx = 220)

                #heading
                label = ttk.Label(self, text ="Enter Files", font = LARGEFONT)
                label.grid(row = 1, column = 0, padx = 100, pady = 20)

                #Entry Point text
                EPT = ttk.Label(self, text ="Input Snowtopia.exe here: ", font = NORMALFONT)
                EPT.grid(row = 2, column = 0, padx = 5, pady = 5)

                #Entry Point
                Browse = ttk.Button(self, text = "Browse A File",
                command = self.fileDialog)
                Browse.grid(row = 3, column = 0, padx = 5, pady = 5)

                global PathInput
                PathInput = tk.Text(self, font=SMALLFONT, width = 50, height = 1)
                PathInput.grid(row = 4, column = 0)

                #blank space (padding)
                fill2 = ttk.Label(self, text='')
                fill2.grid(row = 5, column = 0, pady=29)
                
                #Next button
                global Page1Next
                Page1Next = ttk.Button(self, text ="Next Page",
                command = lambda : controller.show_frame(Validate))

                Page1Next["state"] = "disabled"
                Page1Next.grid(row = 6, column = 0, padx = 10, pady = 10, sticky=tk.E)

        def fileDialog(self):
                global filename, BasePath, AssemblyPath, ModDataExists

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
                                PathLabel.grid(column = 0, row = 3, sticky = 'E')
                                Page1Next["state"] = "disabled"

                        else:
                                PathLabel = ttk.Label(self, font = NORMALFONT, text = 'valid dir')
                                PathLabel.grid(column = 0, row = 3, sticky = 'E')

                                PathLabel.forget()
                                
                                PathInput.insert('end', filename)

                                Page1Next["state"] = "enabled"

                else:
                        PathLabel = ttk.Label(self, font = NORMALFONT, text = 'invalid dir(1)')
                        PathLabel.grid(column = 1, row = 3, sticky = 'E')
                        Page1Next["state"] = "disabled"

class Validate(tk.Frame):
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)

                #blank space (padding + filling)
                fill1 = ttk.Label(self, text='')
                fill1.grid(row = 0, column = 0, pady=25, padx = 220)

                #heading
                label = ttk.Label(self, text ="Validate", font = LARGEFONT)
                label.grid(row = 1, column = 0, padx = 110, pady = 10)

                WarningLabel = ttk.Label(self, text ="This may take a few moments", font = NORMALFONT)
                WarningLabel.grid(row = 2, column = 0, pady = 5)
                
                #validate button
                ValidateButton = ttk.Button(self, text ="Validate", command = self.Validate)

                ValidateButton.grid(row = 3, column = 0, padx = 10)
                
                #blank space (padding)
                fill2 = ttk.Label(self, text='')
                fill2.grid(row = 4, column = 0, pady=42)

                #Next button
                global Page2Next
                if os.path.exists(ModDataZip):
                        Page2Next = ttk.Button(self, text ="Next Page", command = lambda : controller.show_frame(Configure))
                else:
                        Page2Next = ttk.Button(self, text ="Next Page", command = lambda : controller.show_frame(InstallPage))

                Page2Next['state'] = 'disabled'
                Page2Next.grid(row = 5, column = 0, padx = 10, pady = 10, sticky = tk.E)

        def Validate(self):
                global ChangeLogs, CurrentChangeLog
                CurrentChangeLog = False
                ValidatingLabel = ttk.Label(self, text ="Validated...", font = NORMALFONT)
                ValidatingLabel.grid(row = 3, column = 0, sticky = tk.E)
                
                result = Validator.Validate(AssemblyPath)

                if result == 3891662:
                        ResultLabel = ttk.Label(self, text ="Validated Sucsessfully!", font = NORMALFONT)
                        Page2Next['state'] = 'enabled'
                
                elif os.path.exists(f'{current}\ChangeLogs\{result}.txt'):
                        CurrentChangeLog = f'{result}.txt'
                        ResultLabel = ttk.Label(self, text ="Validated Sucsessfully!(Other mods detected will be overwritten)", font = NORMALFONT)
                        Page2Next['state'] = 'enabled'
                else:
                        ResultLabel = ttk.Label(self, text =f"got {str(result)} which is invalid", font = NORMALFONT)

                ResultLabel.grid(row = 4, column = 0, pady = 5)

class Configure(tk.Frame):
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)

                #blank space (padding + filling)
                fill1 = ttk.Label(self, text='')
                fill1.grid(row = 0, column = 0, pady=0, padx = 220)

                #heading
                label = ttk.Label(self, text ="Configuration - Select maps to install", font = LARGEFONT)
                label.grid(row = 1, column = 0, pady = 10)

                #this gets messy but it's because of having assigments in certain locations
                #selection pane
                opt = tk.Listbox(self, selectmode="multiple")
                opt.grid(row = 4, column = 0, pady = 5)

                #drop-down menu
                options = ['Select...','Top 10', 'Top 25', 'None', 'Custom']

                # datatype of menu text
                clicked = tk.StringVar()

                def UpdateSelectedMaps():
                        global SelectedMaps
                        if clicked.get() == 'Custom':
                                SelectedMaps = opt.selection_get().split('\n')
                        elif clicked.get != 'None':
                                with open('TopMaps.cfg') as f:
                                        if clicked.get() == 'Top 10':
                                                SelectedMaps = f.readlines()[0].split(',')
                                        elif clicked.get() == 'Top 25':
                                                SelectedMaps = f.readlines()[1].split(',')

                #Next button
                NextPage = ttk.Button(self, text ="Next Page", state = 'disabled',
                command = lambda : [UpdateSelectedMaps(), controller.show_frame(InstallPage)])
                
                NextPage.grid(row = 5, column = 0, padx = 10, pady = 10, sticky = tk.E)

                #a bit messy but function has to be here
                def UpdateDropSelection(event):
                        NextPage['state'] = 'enabled'
                        if clicked.get() == 'Custom':
                                opt['state'] = 'normal'
                        else:
                                opt['state'] = 'disabled'

                # Create Dropdown menu
                drop = ttk.OptionMenu(self, clicked, *options, command = UpdateDropSelection)
                drop.grid(row = 3, column = 0, pady = 7)

                #inflate map selection
                for i in maps:
                        opt.insert(tk.END, i)
                
                opt['state'] = 'disabled'

class InstallPage(tk.Frame):
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)

                #blank space (padding + filling)
                fill1 = ttk.Label(self, text='')
                fill1.grid(row = 0, column = 0, pady=25, padx = 220)

                #heading
                label = ttk.Label(self, text ="Install", font = LARGEFONT)
                label.grid(row = 1, column = 0, pady = 10)

                WarningLabel = ttk.Label(self, text ="This may take a few moments", font = NORMALFONT)
                WarningLabel.grid(row = 2, column = 0, padx = 5, pady = 5)

                #Install button
                global InstallButton
                InstallButton = ttk.Button(self, text ="Install", command = self.Install)
                InstallButton.grid(row = 3, column = 0, padx = 10)

                #blank space (padding)
                fill2 = ttk.Label(self, text='')
                fill2.grid(row = 4, column = 0, pady=42)

                #next
                global FinalNext
                FinalNext = ttk.Button(self, text ="Next Page", state = "disabled",
                command = lambda : controller.show_frame(FinalPage))

                FinalNext.grid(row = 5, column = 0, padx = 10, pady = 10, sticky = tk.E)

        def Install(self):
                ValidatingLabel = ttk.Label(self, text ="Process finished!", font = NORMALFONT)
                ValidatingLabel.grid(row = 2, column = 0, sticky = tk.E)

                BtoB64.Convert(AssemblyPath)

                if CurrentChangeLog != False:
                        AssemblyPatch.Patch(f'ChangeLogs/{CurrentChangeLog}', "Assembly-CSharp.txt.b64")
                
                AssemblyPatch.Patch('ChangeLogs/Install.txt', "NewAssembly.txt.b64")
                B64toB.Convert(AssemblyPath)

                if os.path.exists(ModDataZip):
                        if os.path.exists(f'{BasePath}/ModData'):
                                shutil.rmtree(f'{BasePath}/ModData')          
                        with zipfile.ZipFile(ModDataZip, 'r') as zip_ref: 
                                zip_ref.extractall(f'{BasePath}/ModData')
                        
                        for m in SelectedMaps:
                                if not os.path.exists(f'{BasePath}/ModData/maps/{m}'):
                                        shutil.copytree(f'maps/{m}', f'{BasePath}/ModData/maps/{m}')

                FinalNext['state'] = 'enabled'
                InstallButton['state'] = 'disabled'

                os.remove("Assembly-CSharp.txt.b64")
                os.remove("NewAssembly.txt.b64")

                ResultLabel = ttk.Label(self, text ="Installed Sucsessfully!", font = NORMALFONT)
                ResultLabel.grid(row = 4, column = 0)


class FinalPage(tk.Frame):
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)
                label = ttk.Label(self, text ="Thanks for Installing!", font = LARGEFONT)
                label.grid(row = 0, column = 0, padx = 80, pady = 70)

                # button to show frame 2 with text
                # layout2
                button1 = ttk.Button(self, text ="Exit", command = sys.exit)

                #blank space (padding)
                fill2 = ttk.Label(self, text='')
                fill2.grid(row = 1, column = 0, pady=45, padx = 220)

                # putting the button in its place by
                # using grid
                button1.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = 'E')

# Driver Code
app = tkinterApp()
app.mainloop()