# module installer

## Configuration
required_modules = ["colorama", "requests"]

BaseURL = "https://raw.githubusercontent.com/Greenloop36/PIP-Module-Installer/master/"
FilesToInstall = ["pmi.py", "Version.txt", "README.md"]
ThisVersion = "2.1"

### init
print("initialising...")
import sys
import subprocess
import os
import webbrowser

## Core Methods
def YesNo(prompt: str = None) -> bool:
    print(prompt,"(Y/n)")

    while True:
        selection: str = input("> ")
        selection = selection.lower()

        if selection == "y":
            return True
        elif selection == "n":
            return False

def InstallModule(Name: str) -> tuple[bool, str, int]:
    result = subprocess.run(['cmd', '/c', f'pip install {Name}'], shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        return True, result.stdout, result.returncode
    else:
        return False, result.stderr, result.returncode

def IsModuleInstalled(Name: str) -> bool:
    a = None
    Installed: bool = None

    try:
        a = __import__(Name)
    except ModuleNotFoundError:
        Installed = False
    else:
        Installed = True
    finally:
        a = None
        return Installed

def ClearWindow() -> None:
    os.system("cls")

def Pause() -> None: # Wait for a key press
    os.system("pause")

def Quit(Message: str | None = None):
    if Message:
        print(f"\n{Message}")
    
    print("\n\nThe program will now exit.")
    Pause()
    sys.exit(0)


def Settings_Get(Key: str = None) -> any: ## None if key does not exist, Leave 1st argument (Key) blank for the entire settings file (dict)
    File = open("pmi_settings.json", "r")
    Parsed = json.loads(File.read())
    File.close()

    if Key != None:
        return Parsed[Key] or None
    else:
        return Parsed

def Settings_Set(Key: str, Value: any):
    File = open("pmi_settings.json", "w")

    Settings = Settings_Get()
    Settings[Key] = Value
    Settings = json.dumps(Settings)

    File.write(Settings)
    File.close()


## Initial Checks
# print("init settings...")
# try:
#     open("pmi_settings.json", "x")
# except FileExistsError as e:
#     print("\t| file already exists, continuing.")
# except Exception as e:
#     Quit(f"(Fatal error!) Could not create the settings file.\n{e}")

init_modules_to_install = []
print("checking dependencies...")

# Check required dependencies
for module in required_modules:
    print(f"\t| checking {module}... ", end = "")
    if not IsModuleInstalled(module):
        print("not installed")
        init_modules_to_install.append(module)
    else:
        print("installed")

ClearWindow()

# Install required modules (if necessary)
if len(init_modules_to_install) > 0:
    print(f"\nThe required modules will now be installed automatically.")

    for module in init_modules_to_install:
        print(f"\t| installing {module}... ", end = "")

        Success, Result, ExitCode = InstallModule(module)

        if Success:
            print("OK")
        else: # Quit on fail
            print("FAIL!")
            Quit(f"Failed to install module {module}! {f"(Code {ExitCode}) " or " "}Below is the attributed error message:\n\n{Result}")
    
    print("\nInstallation has now completed.\n")
    Pause()

ClearWindow()

##########################################
## MAIN
##########################################

## variables
import colorama
from colorama import Fore, Back, Style
import json
import requests

## init
colorama.init(autoreset = True)

## functions
def Error(Message: str):
    print(Fore.RED + "error" + Fore.RESET + ": " + str(Message))

def Notice(Message: str):
    print(Fore.MAGENTA + "notice" + Fore.RESET + ": " + str(Message))

def Warning(Message: str):
    print(Style.BRIGHT + Fore.YELLOW + "warning" + Fore.RESET + Style.RESET_ALL + ": " + str(Message))

def CustomException(Message: str):
    print(Fore.LIGHTRED_EX + str(Message) + Fore.RESET)

def PrintList(List: list):
    for i in List:
        print("\t| " + str(i))

def GetFileFromRepo(FileName) -> tuple[bool, str]:
    Response = requests.get(BaseURL +  FileName)

    if Response.status_code == 200: # Success
        return True, Response.text
    else: # Failure
        #print(Response)
        return False, f"HTTP {Response.status_code} ({Response.reason})"

def CheckForUpdates() -> tuple[bool, str | None]: ## True, NewVersion (if update is available) OR False (if no update or if GET failed)
    Success, Result = GetFileFromRepo("Version.txt")

    if Success:
        Result = Result.replace("\n", "")
        if Result == ThisVersion:
            return False, None
        else:
            return True, Result
    else:
        return False, None

def Terminate(): # User initiated exits
    CustomException("Quitting...")
    sys.exit(0)

def Update(Force: bool = False):
    DownloadCache = {}
    LatestVersion = None

    def CancelInstall(Message: str | None = None):
        nonlocal DownloadCache
        DownloadCache.clear()
        DownloadCache = None

        if Message:
            CustomException(f"Update cancelled: {Message}")
        else:
            CustomException("Update cancelled.")
    
    print("Preparing to update...")

    ## Get latest version
    Success, Result = GetFileFromRepo("Version.txt")
    LatestVersion = Result.replace("\n", "")

    if not Success:
        Error(f"Could not retrieve latest version! ({Result})")
        CancelInstall()
        return
    elif LatestVersion == ThisVersion and not Force:
        return CancelInstall(f"This version, {ThisVersion}, is already the latest available installation for PIP Module Installer.")
    
    LatestVersion = Result.replace("\n", "")
    
    ## Download files
    ClearWindow()
    print("\nDownloading files...")
    for File in FilesToInstall:
        print(f"\t| downloading \"{Fore.LIGHTBLUE_EX}{File}{Fore.RESET}\": ", end = "")
        Success, Result = GetFileFromRepo(File)

        if Success:
            DownloadCache[File] = Result
            print(f"{Fore.GREEN}OK{Fore.RESET}")
        else:
            print(f"{Fore.LIGHTRED_EX}FAIL!{Fore.RESET}")
            return CancelInstall(f"Failed to install \"{File}\"! ({Result})")
    print("Download successful.")
    
    ## Remove old files
    print("\nRemoving old installation...")
    for File in FilesToInstall:
        print(f"\t| removing \"{Fore.LIGHTBLUE_EX}{File}{Fore.RESET}\": ", end = "")

        try:
            os.remove(File)
        except FileNotFoundError:
            print(f"{Fore.YELLOW}NOT FOUND{Fore.RESET}")
        except PermissionError:
            print(f"{Fore.LIGHTRED_EX}FAIL!{Fore.RESET}")
            return CancelInstall(f"Failed to remove the file \"{File}\" because the application has insufficient permissions. Try running in administrator mode.")
        else:
            print(f"{Fore.GREEN}OK{Fore.RESET}")
    print("Old installation files were removed successfully.")

    ## Replace with new files
    print("\nInstalling new files...")
    for Name, Content in DownloadCache.items():
        print(f"\t| installing \"{Fore.LIGHTBLUE_EX}{Name}{Fore.RESET}\": ", end = "")
        
        try:
            File = open(Name, "w")
            File.write(Content)
            File.close()
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}FAIL!{Fore.RESET}")
            return CancelInstall(f"Failed to install the file \"{File}\"!\n{e}")
        else:
            print(f"{Fore.GREEN}OK{Fore.RESET}")
    
    ## Finish
    print("Installation successful.\n")
    Quit(f"PIP Module Installer has been updated to Release {LatestVersion.replace("\n", "")}. Please restart the application.")
        
## commands
class Container_Commands:
    def install(*args):
        ## variables
        ModuleName = args[1]

        ## check
        if ModuleName == "":
            return Error("Missing required argument #1 (ModuleName)!")

        ## install
        print(f"\tInstalling {Fore.BLUE}{str(ModuleName)}{Fore.RESET}...", end = "")
        Success, Result, ExitCode = InstallModule(ModuleName)

        ## result
        if Success:
            print(f"{Fore.GREEN} OK")
        else:
            print(f"{Fore.RED} FAILED\n")
            Error(f"Failed to install {Fore.BLUE}{ModuleName}{Fore.RESET}!\n\t| {Style.DIM}{Result.replace("\n", f"\n\t{Style.RESET_ALL}|{Style.DIM} ")}{Style.RESET_ALL}(Exit code {ExitCode})")
    
    def uninstall(*args):
        ## variables
        ModuleName = args[1]

        ## check
        if ModuleName == "":
            return Error("Missing required argument #1 (ModuleName)!")
        
        ## uninstall
        print(f"\tRemoving {Fore.BLUE}{ModuleName}{Fore.RESET}...", end = "")
        Result = subprocess.run(['cmd', '/c', f'pip uninstall {ModuleName} --yes'], shell=True, capture_output=True, text=True)
        #Result = subprocess.run(f"pip uninstall {ModuleName}")

        ## result
        if Result.returncode != 0:
            #Error(f"Failed to remove {Fore.BLUE}{ModuleName}{Fore.RESET}! (Exit code {Result.returncode})")
            print(f"{Fore.RED} FAILED\n")
            Error(f"Failed to install {Fore.BLUE}{ModuleName}{Fore.RESET}!\n\t| {Style.DIM}{Result.stderr.replace("\n", f"\n\t{Style.RESET_ALL}|{Style.DIM} ")}{Style.RESET_ALL}(Exit code {Result.returncode})")
    
        else:
            if Result.stderr.find("WARNING") != -1:
                print(f"{Fore.YELLOW} NOT FOUND")
            else:
                print(f"{Fore.GREEN} OK")

    def clear(*args):
        ClearWindow()
    
    def exit(*args):
        Terminate()
    
    def list(*args):
        ## variables
        ListName: str = args[1]
        ToPrint: str | None = None

        if ListName == "":
            return Error("Missing required argument #1 (ListName)!")

        ## check
        if ListName.lower() == "commands":
            ToPrint = [attr for attr in dir(Commands) if callable(getattr(Commands, attr)) and not attr.startswith("__")]

        ## out
        if ToPrint:
            print(f"list \"{Fore.BLUE}{ListName}{Fore.RESET}\":")
            PrintList(ToPrint)
        else:
            Error(f"The list \"{Fore.BLUE}{ListName}{Fore.RESET}\" does not exist.")
    
    def upgrade(*args):
        ## variables
        ModuleName = args[1]

        ## check
        if ModuleName == "":
            return Error("Missing required argument #1 (ModuleName)!")

        ## upgrade
        print(f"\tUpdating {Fore.BLUE}{str(ModuleName)}{Fore.RESET}...", end = "")
        Success, Result, ExitCode = InstallModule(f"-U {ModuleName}")

        ## result
        if Success:
            print(f"{Fore.GREEN} OK")
        else:
            print(f"{Fore.RED} FAILED\n")
            Error(f"Failed to upgrade {Fore.BLUE}{ModuleName}{Fore.RESET}!\n\t| {Style.DIM}{Result.replace("\n", f"\n\t{Style.RESET_ALL}|{Style.DIM} ")}{Style.RESET_ALL}(Exit code {ExitCode})")

    def get(*args):
        ## variables
        ModuleName = args[1]

        ## check
        if ModuleName == "":
            return Error("Missing required argument #1 (ModuleName)!")
        
        ## get
        Result = subprocess.run(f"pip show {ModuleName}")

        ## result
        if Result.returncode != 0:
            Error(f"Could not get information for \"{Fore.BLUE}{ModuleName}{Fore.RESET}\"! The module might not be installed.")
    
    def run(*args):
        cmd = args[1]
        silent = False

        if len(args) == 3:
            silent = args[2]

        if cmd == "":
            return Error("Missing required argument #1 (Command)!")
        
        ## run
        if not silent:
            print(f"{Fore.MAGENTA}${Fore.RESET} {cmd}\n")
        
        try:
            Result = subprocess.run(cmd)
        except FileNotFoundError:
            Error("Command execution failed (command not found).")
        except Exception as e:
            return Error(f"(internal error) Command execution failed.\n\t| {Style.DIM}{e}")
        else:
            ## result
            if Result.returncode != 0:
                Warning(f"Command failed:\n\t| Exit code {Result.returncode}")
        
        print()
    
    def runl(*args):
        Notice("You are entering run loop mode.\n\t| \"exit\" to escape;\n\t| \"cls\" to clear the window.\n")

        while True:
            try:
                cmd = input(f"{Fore.MAGENTA}${Fore.RESET} ")
            except KeyboardInterrupt:
                break
            except EOFError:
                break


            if cmd.lower() == "exit":
                break
            elif cmd.lower() == "cls":
                ClearWindow()
            else:
                Commands.run(cmd, True)
    
    def echo(*args):
        print(args[1])
    
    def verify(*args):
        print("Verifying the integrity of installed modules...\n")
        subprocess.run(f"pip check")
    
    def update(*args):
        if args[1] == "--force" or args[1] == "-f":
            Update(True)
        else:
            if YesNo("Do you want to update PIP Module Installer?"):
                print()
                Update()
    
    def releases(*args):
        Notice(f"Redirecting to: \"{Fore.LIGHTBLUE_EX}https://github.com/Greenloop36/PIP-Module-Installer/releases{Fore.RESET}\"...")
        webbrowser.open("https://github.com/Greenloop36/PIP-Module-Installer/releases")

## Main
print("Checking for updates...")
IsUpdateAvailable, NewVersion = CheckForUpdates()

Commands = Container_Commands()
ClearWindow()
print(f"PIP Module Installer [Version {ThisVersion}]\n")
if IsUpdateAvailable:
    Notice(f"An update is available (Version {Fore.LIGHTRED_EX}{ThisVersion}{Fore.RESET} -> {Fore.LIGHTGREEN_EX}{NewVersion}{Fore.RESET})! Run \"update\" to install it.")

while True:
    ## Input
    try:
        inp = input(f"{Fore.YELLOW}<{os.getlogin()}$pmi>{Fore.RESET} ")
    except KeyboardInterrupt:
        CustomException("\nKeyboard Interruption")
        Terminate()
    except EOFError:
        CustomException("\nEnd of File")
        Terminate()

    ## Ignore Blank
    if inp == "" or inp.startswith(" "):
        continue

    ## Parse
    command = inp.split(" ")[0]
    args = inp[len(command) + 1:]

    ## Get Method
    Method = getattr(Commands, command, None)
    
    ## Execute Command
    if callable(Method):
        #Method(args)
        try:
            Method(args)
        except Exception as e:
            print()
            CustomException(f"An exception occurred whilst running the command {Fore.BLUE}{command}{Fore.RED}!\n{Fore.RESET}{Style.DIM}{e}{Style.RESET_ALL}")
    else:
        CustomException(f"\"{command}\" is not recognised as an internal command.\n Use the \"list commands\" command to view the available commands.")

    print()
