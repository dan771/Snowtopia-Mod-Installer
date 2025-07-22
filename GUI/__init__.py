import tkinter as tk
from tkinter import DISABLED, Canvas, Scrollbar, ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk

import sys
import socket
import os
import threading
import shutil
import webbrowser
import datatable

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
#current = os.path.dirname(sys.executable)
current = os.getcwd()
ChangeLogs = os.listdir(f'{current}/logs/')
CurrentChangeLog = False
SelectedChangeLog = False
ModDataZip = 'Blizzard.zip'
maps = os.listdir(f'{current}/maps/')
SelectedMaps = []
data_table = None

class tkinterApp(tk.Tk):
        # __init__ function for class tkinterApp
        def __init__(self, *args, **kwargs):

                # __init__ function for class Tk
                tk.Tk.__init__(self, *args, **kwargs)
                
                # creating a container
                container = tk.Frame(self)
                container.pack(side = "top", fill = "both", expand = False)
                
                self.geometry('450x325+700+200')
                self.minsize(450, 325)
                self.title('Snowtopia Mod Installer')

                self.protocol("WM_DELETE_WINDOW", self.on_exit)
                
                # initializing frames to an empty array
                self.frames = {}

                # iterating through a tuple consisting
                # of the different page layouts
                for F in (StartPage, InternetPage, EnterFile, Configure, Validate, InstallPage, FinalPage):
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

        def on_exit(self):
                os._exit(0)

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Blank space
        fill1 = ttk.Label(self, text='')
        fill1.grid(row=0, column=0, pady=10, padx=220)

        # Blizzard image
        original_image = Image.open("blizzard_logo.png")
        resized_image = original_image.resize((160, 90))  # width x height
        self.image = ImageTk.PhotoImage(resized_image)

        image_label = tk.Label(self, image=self.image)
        image_label.grid(row=1, column=0, pady=10)

        # Heading
        heading = ttk.Label(self, text="Startpage", font=LARGEFONT)
        heading.grid(row=2, column=0, padx=15, pady=15)

        # Paragraph
        paragraph = ttk.Label(self, text="Welcome to the Snowtopia Mod installer!", font=NORMALFONT)
        paragraph.grid(row=3, column=0, pady=10, padx=10)

        # Blank space
        fill1 = ttk.Label(self, text='')
        fill1.grid(row=4, column=0, pady=7.5, padx=0)

        # Help link
        helpLink = ttk.Label(self, text="Need Help?", font=('Helveticabold', 10),
                             foreground="blue", cursor="hand2")
        helpLink.grid(row=5, column=0, padx=10, sticky=tk.W)
        helpLink.bind("<Button-1>", lambda e: webbrowser.open_new_tab(
            "https://snowtopia-modders.fandom.com/wiki/Manual_installation_guide"))

        # Next button
        button2 = ttk.Button(self, text="Next Page", command=lambda: (
                controller.show_frame(InternetPage),
                controller.frames[InternetPage].on_show()
        ))
        button2.grid(row=5, column=0, padx=10, pady=10, sticky=tk.E)

class InternetPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Blank space (padding)
        fill1 = ttk.Label(self, text='')
        fill1.grid(row=0, column=0, pady=20, padx=220)

        # Heading
        label = ttk.Label(self, text="Downloading Maps", font=LARGEFONT)
        label.grid(row=1, column=0, padx=15, pady=10)

        # Status label
        self.status_label = ttk.Label(self, text="Checking...", font=NORMALFONT)
        self.status_label.grid(row=2, column=0, pady=5)

        self.download_status_label = ttk.Label(self, text="Waiting for internet connection...", font=NORMALFONT)
        self.download_status_label.grid(row=3, column=0, pady=5)

        self.progress = ttk.Progressbar(self, orient="horizontal", length="400", mode="determinate")
        self.progress.grid(row=4, column=0, pady=5)

        # Blank space (padding)
        fill2 = ttk.Label(self, text='')
        fill2.grid(row=5, column=0, pady=46.5-18)

        # Help link
        helpLink = ttk.Label(self, text="Need Help?", font=('Helveticabold', 10),
                             foreground="blue", cursor="hand2")
        helpLink.grid(row=6, column=0, padx=10, sticky=tk.W)
        helpLink.bind("<Button-1>", lambda e: webbrowser.open_new_tab(
            "https://snowtopia-modders.fandom.com/wiki/Manual_installation_guide"))

        # Next button
        self.next_button = ttk.Button(self, text="Next Page", state="disabled",
                                      command=lambda: controller.show_frame(EnterFile))
        self.next_button.grid(row=6, column=0, padx=10, pady=10, sticky=tk.E)

    def on_show(self):
        # Only start check when page is shown
        threading.Thread(target=self.run_check, daemon=True).start()

    def run_check(self):
        if self.check_internet():
            self.status_label.config(text="Internet connection available")
            self.download_status_label.config(text="Fetching datatable...")
            self.download()
        else:
            self.status_label.config(text="No internet connection detected")
            self.download_status_label.config(text="Press next to continue.")
            self.next_button.config(state="normal")

    def download(self):
        global data_table
        data_table = datatable.fetch_map_data()
        map_links = datatable.get_all_maps_download_links(data_table)
        
        if len(map_links) == 0:
               self.download_status_label.config(text="No maps to download.")
               self.progress["value"] = 100
        else:
                increment = 100 / len(map_links)

                for download_link in map_links:
                        self.download_status_label.config(text="Downloading " + datatable.calculate_file_name(download_link, False))
                        datatable.download_map(download_link)
                        self.progress["value"] += increment
                self.download_status_label.config(text="Download finished")
                
        # do Top Maps.cfg here cuz why not
        top_rated = datatable.get_top_rated_maps(data_table)

        # write to it
        with open("TopMaps.cfg", "w") as f:
               f.write(datatable.list_to_cfg_line(top_rated[0]) + "\n")
               f.write(datatable.list_to_cfg_line(top_rated[1]) + "\n")
               f.write(datatable.list_to_cfg_line(top_rated[2]))

        self.next_button.config(state="normal")

    @staticmethod
    def check_internet(host="8.8.8.8", port=53, timeout=3):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            return False


    @staticmethod
    def check_internet(host="8.8.8.8", port=53, timeout=3):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            return False


class EnterFile(tk.Frame):
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
                PathInput = tk.Text(self, font=SMALLFONT, state="disabled", width = 50, height = 1)
                PathInput.grid(row = 4, column = 0)

                #blank space (padding)
                fill2 = ttk.Label(self, text='')
                fill2.grid(row = 5, column = 0, pady=30)
                
                #help link
                helpLink = ttk.Label(self, text="Need Help?",font=('Helveticabold', 10),foreground = "blue", cursor="hand2")
                helpLink.grid(row = 6, column = 0, padx = 10, sticky = tk.W)

                #make text an actual link
                helpLink.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://snowtopia-modders.fandom.com/wiki/Manual_installation_guide"))

                #Next button
                global Page1Next
                Page1Next = ttk.Button(self, text ="Next Page",
                command = lambda : controller.show_frame(Validate))

                Page1Next["state"] = "disabled"
                Page1Next.grid(row = 6, column = 0, padx = 10, pady = 10, sticky=tk.E)

        def fileDialog(self):
                global AssemblyPath, BasePath
                PathLabel = self.grid_slaves(column = 1, row = 2)
                for i in PathLabel:
                        i.destroy()

                PathInput.configure(state = "normal")
                PathInput.delete('1.0', 'end')

                init_dir = "/"

                test_path = r"C:\Program Files (x86)\Steam\steamapps\common\Snowtopia"
                if (os.path.exists(f"{test_path}\\Snowtopia.exe")):
                        init_dir = test_path

                filename = filedialog.askopenfilename(initialdir =  init_dir, title = "Select A File", filetype = (("Snowtopia File","*.exe"),("all files","*.*")) )
                
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
                
                PathInput.configure(state = "disabled")

class Validate(tk.Frame):
        global ChangeLogs
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

                def Start_Validation():
                        ValidateThread = threading.Thread(target=Validate.ValidateCheck, args=(self, parent, controller))
                        ValidateThread.start()

                #validate button
                global ValidateButton
                ValidateButton = ttk.Button(self, text ="Validate", command = Start_Validation)
                
                ValidateButton.grid(row = 3, column = 0, padx = 10)
                
                #blank space (padding)
                fill2 = ttk.Label(self, text='')
                fill2.grid(row = 4, column = 0, pady=44)

                #help link
                helpLink = ttk.Label(self, text="Need Help?",font=('Helveticabold', 10),foreground = "blue", cursor="hand2")
                helpLink.grid(row = 5, column = 0, padx = 10, sticky = tk.W)

                #make text an actual link
                helpLink.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://snowtopia-modders.fandom.com/wiki/Manual_installation_guide"))

                #Next button
                global Page2Next
                if os.path.exists(ModDataZip):
                        Page2Next = ttk.Button(self, text ="Next Page", command = lambda : controller.show_frame(Configure))
                else:
                        Page2Next = ttk.Button(self, text ="Next Page", command = lambda : controller.show_frame(InstallPage))

                Page2Next['state'] = 'disabled'
                Page2Next.grid(row = 5, column = 0, padx = 10, pady = 10, sticky = tk.E)

        def ValidateCheck(self, parent, controller):
                global CurrentChangeLog
                CurrentChangeLog = False
                ValidatingLabel = ttk.Label(self, text ="Validating...", font = NORMALFONT)
                ValidateButton["state"] = "disabled"
                ValidatingLabel.grid(row = 3, column = 0, sticky = tk.E)
                
                result = Validator.Validate(AssemblyPath)
                avalanche_results = [3891662, 3958872, 3968837, 3968928, 3982742, 3990400, 4001520, 4033672, 4033672, 4037915, 4048389, 4049907, 4077684, 4077901, 4078018]

                if result in avalanche_results:
                        ResultLabel = ttk.Label(self, text = f"Please upgrade your Snowtopia Version! {result}", font = NORMALFONT)

                #if result == 3891662:
                #        ResultLabel = ttk.Label(self, text ="Validated Sucsessfully!", font = NORMALFONT)
                #        ConfigOverwriteBox['state'] = "disabled"
                #        Page2Next['state'] = 'enabled'
                #
                if os.path.exists(f'{current}\\logs\\{result}.sbc'):
                        CurrentChangeLog = f'{result}.sbc'
                        ResultLabel = ttk.Label(self, text ="Validated Sucsessfully!", font = NORMALFONT)
                        Page2Next['state'] = 'enabled'

                        # Uhh? Don't think it's important for blizzarrd.
                        #with open('ForceOverwrite.cfg', 'r') as ForceOverwriteFile:
                        #        ForceOverwriteLines = ForceOverwriteFile.readlines()
                        #        ConfigOverwriteBox['state'] = "normal"
                        #        for ForceOverwriteLine in ForceOverwriteLines:
                        #                if not(str(result) in ForceOverwriteLine):
                        #                        continue
                        #                if "overwrite" in ForceOverwriteLine:
                        #                        ConfigOverwriteBox['state'] = "disabled"
                        #                break
                else:
                        ResultLabel = ttk.Label(self, text =f"got {str(result)} which is invalid", font = NORMALFONT)

                ResultLabel.grid(row = 4, column = 0, pady = 5)
                ValidateButton["state"] = "enabled"

class Configure(tk.Frame):
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)

                #blank space (padding + filling)
                fill1 = ttk.Label(self, text='')
                fill1.grid(row = 0, column = 0, pady=0, padx = 220)

                #heading
                label = ttk.Label(self, text ="Configuration - Select maps to install", font = LARGEFONT)
                label.grid(row = 1, column = 0, pady = 5)

                #selection canvas
                base = tk.Canvas(self)
                base.grid(row = 4, column = 0)

                #scrollbar for opt (Listbox)
                scroll = Scrollbar(base)
                scroll.pack(side=tk.RIGHT, fill=tk.Y)

                #this gets messy but it's because of having assigments in certain locations
                #selection pane
                opt = tk.Listbox(base, selectmode="multiple")
                opt.pack()

                #applying scrollbar to ListBox (opt)
                opt.config(yscrollcommand=scroll.set)
                scroll.config(command=opt.yview)

                #drop-down menu
                options = ['Select...','Top 10', 'Top 25', 'Top 50', 'All', 'None', 'Custom']

                # datatype of menu text
                clicked = tk.StringVar()

                def UpdateSelectedMaps(): #this gets called when next button is pressed and basically configures selection for install
                        global SelectedMaps
                        SelectedMaps = opt.selection_get().split('\n')

                #Next button
                NextPage = ttk.Button(self, text ="Next Page", state = 'disabled',
                command = lambda : [UpdateSelectedMaps(), controller.show_frame(InstallPage)])
                
                NextPage.grid(row = 6, column = 0, padx = 10, pady = 10, sticky = tk.E)

                #a bit messy but these functions have to be here
                def UpdateDropSelection(event):
                        clicked.set("Custom")
                        NextPage['state'] = 'enabled'

                opt.bind('<<ListboxSelect>>', UpdateDropSelection)

                def UpdateDropSelectionMaps(event):
                        if clicked.get() != 'Select...':
                                NextPage['state'] = 'enabled'
                        if clicked.get() == 'None':
                                opt.select_clear(0, tk.END)
                                return
                        if clicked.get() == 'All':
                                opt.select_set(0, tk.END)
                                return
                        with open('TopMaps.cfg') as f:
                                if clicked.get() == 'Top 10':
                                        opt.select_clear(0, tk.END)
                                        Top10Maps = f.readlines()[0].split(',')
                                        Top10Maps[-1] = Top10Maps[-1][:-1]
                                        for select in Top10Maps:
                                                opt.select_set(maps.index(select))
                                        return
                                if clicked.get() == 'Top 25':
                                        opt.select_clear(0, tk.END)
                                        Top25Maps = f.readlines()[1].split(',')
                                        Top25Maps[-1] = Top25Maps[-1][:-1]
                                        for select in Top25Maps:
                                                opt.select_set(maps.index(select))
                                        return
                                if clicked.get() == 'Top 50':
                                        opt.select_clear(0, tk.END)
                                        Top50Maps = f.readlines()[2].split(',')
                                        for select in Top50Maps:
                                                opt.select_set(maps.index(select))
                                        return

                # Create Dropdown menu
                drop = ttk.OptionMenu(self, clicked, *options, command = UpdateDropSelectionMaps)
                drop.grid(row = 3, column = 0, pady = 7)

                #inflate map selection
                for i in maps:
                        opt.insert(tk.END, i)

                #padding
                padding = ttk.Label(self, text="")
                padding.grid(row = 5, column = 0, pady = 2)

                #help box (for both help and selection of maps)
                helpBox = Canvas(self)
                helpBox.grid(row = 6, column = 0, padx = 10, sticky = tk.W)

                #help link
                helpLink = ttk.Label(helpBox, text="Need Help?",font=('Helveticabold', 10),foreground = "blue", cursor="hand2")
                helpLink.grid(row=0, column=0, padx=10)

                #make text an actual link
                helpLink.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://snowtopia-modders.fandom.com/wiki/Manual_installation_guide"))

                #maps link
                mapLink = ttk.Label(helpBox, text="Browse maps",font=('Helveticabold', 10),foreground = "blue", cursor="hand2")
                mapLink.grid(row=0, column=1, padx=10)

                #make text an actual link
                mapLink.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.snowtopiamodding.com"))

class InstallPage(tk.Frame):
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)

                #blank space (padding + filling)
                fill1 = ttk.Label(self, text='')
                fill1.grid(row = 0, column = 0, pady=20, padx = 220)

                #heading
                label = ttk.Label(self, text ="Install", font = LARGEFONT)
                label.grid(row = 1, column = 0, pady = 10)

                WarningLabel = ttk.Label(self, text ="This may take a few moments", font = NORMALFONT)
                WarningLabel.grid(row = 2, column = 0, padx = 5, pady = 5)

                global ConfigOverwrite, ConfigOverwriteBox
                ConfigOverwrite = tk.BooleanVar()
                ConfigOverwrite.set(True)
                ConfigOverwriteBox = ttk.Checkbutton(self, text="Overwrite config files", variable=ConfigOverwrite, onvalue=True, offvalue=False, state=DISABLED)
                ConfigOverwriteBox.grid(row = 4, column = 0, padx = 5, pady = 5)

                #if not(os.path.exists(f'{BasePath}/ModData/balance.cfg') and os.path.exists(f'{BasePath}/ModData/basic.cfg') and os.path.exists(f'{BasePath}/ModData/construction.cfg') and os.path.exists(f'{BasePath}/ModData/economy.cfg')):
                #        ConfigOverwriteBox['state']  = 'disabled'

                #Install button
                global InstallButton
                InstallThread = threading.Thread(target=InstallPage.Install, args=(self, parent, controller))
                InstallButton = ttk.Button(self, text ="Install", command = InstallThread.start)
                InstallButton.grid(row = 5, column = 0, padx = 10, pady = 10)

                global ProgressText
                ProgressText = ttk.Label(self, text='Not started: 0%')
                ProgressText.grid(row = 6, column = 0, padx = 25, pady = 0, sticky = tk.W)

                global ProgressBar
                ProgressBar = ttk.Progressbar(self, orient="horizontal", length="400", mode="determinate")
                ProgressBar.grid(row = 7, column = 0, pady = 0)

                #blank space (padding)
                fill2 = ttk.Label(self, text='')
                fill2.grid(row = 8, column = 0, pady=2)

                #help link
                helpLink = ttk.Label(self, text="Need Help?",font=('Helveticabold', 10),foreground = "blue", cursor="hand2")
                helpLink.grid(row=9, column=0, padx=10, sticky=tk.W)

                #make text an actual link
                helpLink.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://snowtopia-modders.fandom.com/wiki/Manual_installation_guide"))

                #next
                global FinalNext
                FinalNext = ttk.Button(self, text ="Next Page", state = "disabled",
                command = lambda : controller.show_frame(FinalPage))

                FinalNext.grid(row = 9, column = 0, padx = 10, pady = 10, sticky = tk.E)

        def Install(self, parent, controller):
                ConfigOverwriteBox['state'] = 'disabled'
                InstallButton['state'] = 'disabled'
                ProgressText.config(text="Progess... 0%")#(os.path.exists(f'{BasePath}/Blizzard'))
                incriment = (1 / (4 + 2*(os.path.exists(ModDataZip)))) * 100

                ProgressText.config(text=f'Converting Assembly to B64... {round(ProgressBar["value"])}%')
                BtoB64.Convert(AssemblyPath) #1
                ProgressBar['value'] += incriment

                #if CurrentChangeLog != False:
                #        ProgressText.config(text=f'Uninstalling old Assembly... {round(ProgressBar["value"])}%')
                #        AssemblyPatch.Patch(f'ChangeLogs/{CurrentChangeLog}', "Assembly-CSharp.txt.b64") #?
                #        ProgressBar['value'] += incriment
                
                ProgressText.config(text=f'Installing new Assembly... {round(ProgressBar["value"])}%')
                AssemblyPatch.Patch(f'logs/{CurrentChangeLog}', "NewAssembly.txt.b64") #2
                ProgressBar['value'] += incriment

                ProgressText.config(text=f'Applying Patches... {round(ProgressBar["value"])}%')
                B64toB.Convert(AssemblyPath) #3
                ProgressBar['value'] += incriment

                balanceCfg, basicCfg, constructionCfg, economyCfg = '', '', '', ''

                if os.path.exists(ModDataZip):
                        #if os.path.exists(f'{BasePath}/ModData'):
                        #        if ConfigOverwrite.get() == False:
                        #                ProgressText.config(text=f'Saving old configs... {round(ProgressBar["value"])}%')

                        #                with open(f'{BasePath}/ModData/balance.cfg', 'r') as balanceCfgFile:
                        #                        balanceCfg = balanceCfgFile.read()

                        #                with open(f'{BasePath}/ModData/basic.cfg', 'r') as basicCfgFile:
                        #                        basicCfg = basicCfgFile.read()

                        #                with open(f'{BasePath}/ModData/construction.cfg', 'r') as constructionCfgFile:
                        #                       constructionCfg = constructionCfgFile.read()

                        #               with open(f'{BasePath}/ModData/economy.cfg', 'r') as economyCfgFile:
                        #                       economyCfg = economyCfgFile.read()

                        #               ProgressBar['value'] += incriment

                        #       ProgressText.config(text=f'Removing old ModData... {round(ProgressBar["value"])}%')
                        #       shutil.rmtree(f'{BasePath}/ModData') #?
                        #       ProgressBar['value'] += incriment


                        with zipfile.ZipFile(ModDataZip, 'r') as zip_ref: 
                                ProgressText.config(text=f'Extracting ModData... {round(ProgressBar["value"])}%')
                                zip_ref.extractall(f'{BasePath}/Blizzard') #?
                                ProgressBar['value'] += incriment
                        
                        #if balanceCfg != '':
                        #        ProgressText.config(text=f'Loading saved configs... {round(ProgressBar["value"])}%')
                        #        
                        #        with open(f'{BasePath}/ModData/balance.cfg', 'w') as balanceCfgFile:
                        #                balanceCfgFile.write(balanceCfg)

                        #       with open(f'{BasePath}/ModData/basic.cfg', 'w') as basicCfgFile:
                        #               basicCfgFile.write(basicCfg)
                                
                        #       with open(f'{BasePath}/ModData/construction.cfg', 'w') as constructionCfgFile:
                        #               constructionCfgFile.write(constructionCfg)

                        #       with open(f'{BasePath}/ModData/economy.cfg', 'w') as economyCfgFile:
                        #               economyCfgFile.write(economyCfg)

                        #       ProgressBar['value'] += incriment

                        ProgressText.config(text=f'Adding maps... {round(ProgressBar["value"])}%')
                        for m in SelectedMaps: #?
                                if not os.path.exists(f'{BasePath}/Blizzard/Maps/{m}'):
                                        shutil.copytree(f'maps/{m}', f'{BasePath}/Blizzard/Maps/{m}')
                        ProgressBar['value'] += incriment

                FinalNext['state'] = 'enabled'

                #cleanup - 4
                ProgressText.config(text=f'Cleaning up... {round(ProgressBar["value"])}%')
                os.remove("Assembly-CSharp.txt.b64")
                os.remove("NewAssembly.txt.b64")
                if os.path.exists("False"):
                        shutil.rmtree("False")
                ProgressBar['value'] += incriment
                ProgressText.config(text='Installed Successfully!')


class FinalPage(tk.Frame):
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)
                label = ttk.Label(self, text ="Thanks for Installing Blizzard!", font = LARGEFONT)
                label.grid(row = 0, column = 0, padx = 80, pady = 70)

                # button to show frame 2 with text
                # layout2
                button1 = ttk.Button(self, text ="Exit", command = self.on_exit)

                #blank space (padding)
                fill2 = ttk.Label(self, text='')
                fill2.grid(row = 1, column = 0, pady=45, padx = 220)

                # putting the button in its place by
                # using grid
                button1.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = 'E')

        def on_exit(self):
                os._exit(0)

# Driver Code
app = tkinterApp()
app.mainloop()
