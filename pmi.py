# module installer

## Configuration
required_modules = ["colorama"]

### init
print("initialising...")
import sys
import subprocess
import os

## Core Methods
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
        Result = subprocess.run(f"pip uninstall {ModuleName}")

        ## result
        if Result.returncode != 0:
            Error(f"Failed to remove {Fore.BLUE}{ModuleName}{Fore.RESET}! (Exit code {Result.returncode})")

    def clear(*args):
        ClearWindow()
    
    def exit(*args):
        sys.exit(0)
    
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
            cmd = input(f"{Fore.MAGENTA}${Fore.RESET} ")

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

## Main
Commands = Container_Commands()
print("PIP Module Installer [Version 2.0]\n")

while True:
    ## Input
    inp = input(f"{Fore.YELLOW}<{os.getlogin()}$pmi>{Fore.RESET} ")

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
        Method(args)
        try:
            pass
        except Exception as e:
            print()
            Error(f"An exception occurred when processing the command {Fore.BLUE}{command}{Fore.RESET}!\n{Style.DIM}{e}{Style.RESET_ALL}")
    else:
        CustomException(f"\"{command}\" is not recognised as an internal command.\n Use the \"list commands\" command to view the available commands.")

    print()
