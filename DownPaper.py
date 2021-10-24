###################################################################################################################################################
#####                                                                     ########                                                            #####
####         _____                      _____                              ######          ▄████  ▄▄▄       ███▄ ▄███▓▓█████     ██ ▄█▀        ####
###         |  __ \                    |  __ \                              ####          ██▒ ▀█▒▒████▄    ▓██▒▀█▀ ██▒▓█   ▀     ██▄█▒          ###
##          | |  | | _____      ___ __ | |__) |_ _ _ __   ___ _ __           ##          ▒██░▄▄▄░▒██  ▀█▄  ▓██    ▓██░▒███      ▓███▄░           ##
##          | |  | |/ _ \ \ /\ / / '_ \|  ___/ _` | '_ \ / _ \ '__|          ##          ░▓█  ██▓░██▄▄▄▄██ ▒██    ▒██ ▒▓█  ▄    ▓██ █▄           ##
##          | |__| | (_) \ V  V /| | | | |  | (_| | |_) |  __/ |             ##          ░▒▓███▀▒ ▓█   ▓██▒▒██▒   ░██▒░▒████▒   ▒██▒ █▄          ##
##          |_____/ \___/ \_/\_/ |_| |_|_|   \__,_| .__/ \___|_|             ##           ░▒   ▒  ▒▒   ▓▒█░░ ▒░   ░  ░░░ ▒░ ░   ▒ ▒▒ ▓▒          ##
###                                               | |                       ####           ░   ░   ▒   ▒▒ ░░  ░      ░ ░ ░  ░   ░ ░▒ ▒░         ###
####                                              |_|                      ######        ░ ░   ░   ░   ▒   ░      ░      ░      ░ ░░ ░         ####
#####                                                                     ########             ░       ░  ░       ░      ░  ░   ░  ░          #####
###################################################################################################################################################

import time
import os, sys
import zipfile
import tkinter
import requests
import clipboard
import subprocess
import tkinter.messagebox

from selenium import webdriver
from requests_futures.sessions import FuturesSession
from webdriver_manager.firefox import GeckoDriverManager
from tkinter import filedialog, Tk, Button, Entry, StringVar, Canvas


wallpaper_engine_path, directory_ext, config_path, session = None, None, f"{os.getenv('APPDATA')}\\Game_K\\DownPaper", FuturesSession()


def initialisation():
    '''
    ATTENTION
    =========

    Ne pas séléctionner "wallpaper_engine\launcher.exe"
    (il peut avoir des erreurs au lancement)

    Séléctionner soit:
        - wallpaper32.exe
        - wallpaper64.exe
    '''

    global wallpaper_engine_path, directory_ext, config_path
    os.system('')
    try:
        os.makedirs(config_path)
    except FileExistsError:
        # directory already exists
        pass
    try:
        open(f"{config_path}\\conf.ini", 'r').read()
    except FileNotFoundError:
        open(f"{config_path}\\conf.ini", 'w').write("wallpaper_engine_path=NoPathFind")
    testpath = open(f"{config_path}\\conf.ini", 'r').read().replace("wallpaper_engine_path=", '')
    if not os.path.exists(testpath):
        fen = Tk()
        filename_intput = StringVar()
        def on_closing():
            fen.destroy()
            quit()
        def parcourir():
            filename_intput.set(filedialog.askopenfilename())
        def writepath():
            testpath = str(filename_intput.get()).replace('/', '\\')
            if not os.path.exists(testpath):
                msgbox('Le chemin vers "Wallpaper Engine" est incorrect', 'w')
            else:
                open(f"{config_path}\\conf.ini", 'w').write("wallpaper_engine_path=" + testpath)
                fen.destroy()
        fen.resizable(False, False)
        fen.title("Config Path | Wallpaper Engine")
        fen.protocol("WM_DELETE_WINDOW", on_closing)
        Canvas(fen, width=10, height=10).grid(row=1, column=1)
        Canvas(fen, width=10, height=10).grid(row=5, column=5)
        Entry(fen, textvariable=filename_intput, width=50, bg ='bisque').grid(row=2, column=2) 
        Canvas(fen, width=5, height=5).grid(row=2, column=3)
        Button(fen, text='Parcourir',command=parcourir).grid(row=2, column=4) 
        Canvas(fen, width=5, height=5).grid(row=3, column=4) 
        Button(fen, text=' Terminé ',command=writepath).grid(row=4, column=4)   
        fen.mainloop()
    else:
        pass
    open(f"{config_path}\\conf.ini", 'r').read().replace("wallpaper_engine_path=", '')
    wallpaper_engine_path = testpath
    directory_ext = '\\'.join(wallpaper_engine_path.split('\\')[0:-1]) + "\\projects\\defaultprojects"
    return True

def msgbox(msg, windows):
    title = "Download Wallpaper"
    root = tkinter.Tk()
    root.withdraw()
    if windows == "i" or windows == "info":
        tkinter.messagebox.showinfo(title, msg)
    if windows == "w" or windows == "warning":
        tkinter.messagebox.showwarning(title, msg)
    if windows == "e" or windows == "error":
        tkinter.messagebox.showerror(title, msg)
    root.destroy()

def execute_force(command):
    try:
        driver.switch_to.window(driver.window_handles[0])
        while True:
            try:
                driver.execute_script(command)
                break
            except: pass
    except: pass

def findid(url):
    try:
        idw = url.replace("https://steamcommunity.com/sharedfiles/filedetails/?", "")
        start = idw.index("id=") + len("id=")
        end = idw.index("&", start )
        return idw[start:end]
    except:
        return url.replace("https://steamcommunity.com/sharedfiles/filedetails/?id=", "")

def download(idw):
    data = {"publishedFileId":int(idw),"collectionId":None,"extract":True,"hidden":False,"direct":False,"autodownload":False}
    uuid = str(session.post('https://backend-03-prd.steamworkshopdownloader.io/api/download/request', json=data).result().json())[10:-2]
    statuts = 404
    while statuts != 200:
        File = requests.get(f'https://backend-03-prd.steamworkshopdownloader.io/api/download/transmit?uuid={uuid}')
        statuts = int(File.status_code)
    data = {"uuids":[uuid]}
    error = session.post('https://backend-03-prd.steamworkshopdownloader.io/api/download/status', json=data).result().json()
    if error[uuid]['downloadError'] != '':
        return False, error[uuid]['downloadError']
    open(uuid+'.zip', 'wb').write(File.content)
    return True, uuid

def checkfolder(path : str):
    try:
        os.listdir(path)
        return True
    except:
        return False

def findinfo(idw):
    return session.post('https://backend-03-prd.steamworkshopdownloader.io/api/details/file', json=[int(idw)]).result().json()[0]

def rename(path : str, NewName : str):
    dst = path.split("\\")
    del dst[-1]
    dst.append(NewName.replace("\\", "").replace("/", "").replace(":", "").replace("*", "").replace("?", "").replace('"', "").replace("<", "").replace(">", "").replace("|", ""))
    os.rename(path.replace("\\", "/"), "/".join(dst))

def _reboot(pathapp):
    try:
        subprocess.run(f"taskkill /im wallpaper64.exe /f", capture_output=True, shell=True, encoding="cp437").stdout
        subprocess.run(f"taskkill /im wallpaper32.exe /f", capture_output=True, shell=True, encoding="cp437").stdout
        os.startfile(pathapp)
        return True
    except:
        msgbox("Error 185. La fonction '_reboot' n'a pas fonctionné.\nVérifier le chemin du programme 'Wallpaper Engine'", "w")

def script(url : str):
    idw, error = findid(url), 0
    while True:
        statuts, uuid = download(idw)
        if statuts:
            break
        if not statuts:
            error += 1
        if error > 3:
            msgbox(f"Error 168.No possible download\n\n{uuid}", "e")
            return
    info = findinfo(idw)

    name = info['title'].replace("\\", "").replace("/", "").replace(":", "").replace("*", "").replace("?", "").replace('"', "").replace("<", "").replace(">", "").replace("|", "")
    if checkfolder(f'{directory_ext}\\{name}'):
        INTnbname = 1
        STRnbname = ""
        while checkfolder(f'{directory_ext}\\{name}{STRnbname}'):
            INTnbname = INTnbname + 1
            STRnbname = f" ({INTnbname})"
        os.makedirs(f'{directory_ext}\\{name + STRnbname}')
        path = f'{directory_ext}\\{name + STRnbname}'
        print(f'''\r├───── \033[33mLe dossier a été renommé par "\033[31m{name}{STRnbname}\033[33m" au lieu de "\033[31m{name}\033[33m"\033[0m\n└───── \033[33mDownload...\033[0m''', end="")
    else:
        os.makedirs(f'{directory_ext}\\{name}')
        path = f'{directory_ext}\\{name}'

    with zipfile.ZipFile(uuid+'.zip', 'r') as zip_ref:
        zip_ref.extractall(path)

    if not _reboot(wallpaper_engine_path):
        return
    os.remove(uuid+'.zip')

initialisation()
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
driver.get("https://steamcommunity.com/app/431960/workshop")

while True:
    try:
        if "steamcommunity.com/sharedfiles" in driver.current_url:
            try:
                x = str(driver.execute_script("""return document.querySelector('a[class="header_installsteam_btn_content"]').href"""))
                if x != 'https://github.com/Game-K-Hack':
                    execute_force("""document.querySelector('div[class="rightDetailsBlock"]').innerHTML += '<div class="workshopTags"><span class=\"workshopTagsTitle\">Donwloader:&nbsp;</span><a href=\"https://github.com/Game-K-Hack">Game K</a></div>';""")
                    execute_force("""document.querySelector('div[class="game_area_purchase_game"] h1 span').remove()""")
                    execute_force("""document.querySelector('div[class="game_area_purchase_game"] h1 br').remove()""")
                    execute_force("""document.querySelector('div[class="game_area_purchase_margin"] div[class="game_area_purchase_game"] div').innerHTML = `<a id=\"SubscribeItemBtn\" class=\"btn_green_white_innerfade btn_border_2px btn_medium \"onclick="getElementById('SubscribeItemOptionAdd').innerHTML='Download...'"><div class=\"subscribeIcon\"></div><span class=\"subscribeText\"><div id=\"SubscribeItemOptionAdd\" class=\"subscribeOption subscribe selected\">DownPaper</div></span></a>`""")
                    execute_force("""document.querySelector('title').innerText = 'Wallpaper Downloader'""")
                    execute_force("""document.querySelector('link[rel="shortcut icon"]').href = 'https://cdn.discordapp.com/attachments/837345074877562892/840256392152481792/python.png'""")
                    execute_force("""document.querySelector('a[class="header_installsteam_btn_content"]').innerText = 'Installer DownPaper'""")
                    execute_force("""document.querySelector('a[class="header_installsteam_btn_content"]').href = 'https://github.com/Game-K-Hack'""")
                else:
                    pass
            except:
                pass

            try:
                x = str(driver.execute_script("""return document.querySelector('div[id="SubscribeItemOptionAdd"]').innerText"""))
                if x != 'DownPaper' and "download" not in x.lower() and "finish" not in x.lower():
                    driver.refresh()
            except: pass

            try:
                x = str(driver.execute_script("""return document.querySelector('a[id="SubscribeItemBtn"]').innerText"""))
                if "download" in x.lower():
                    print(f'''\r┌[\033[32m+\033[0m] Find URL: \033[36m{driver.current_url}\033[0m\n└───── \033[33mDownload...\033[0m''', end="")
                    script(driver.current_url)
                    print(f'''\r└───── \033[32mFinish     \033[0m\n\n''')
                    execute_force("""document.querySelector('div[class="game_area_purchase_margin"] div[class="game_area_purchase_game"] div').innerHTML = `<a id=\"SubscribeItemBtn\" class=\"btn_green_white_innerfade btn_border_2px btn_medium \"><div class=\"subscribeIcon\"></div><span class=\"subscribeText\"><div id=\"SubscribeItemOptionAdd\" class=\"subscribeOption subscribe selected\">Finish</div></span></a>`""")
                    execute_force("""document.querySelector('div[class="game_area_purchase_margin"] div[class="game_area_purchase_game"] div').innerHTML = `<a id=\"SubscribeItemBtn\" class=\"btn_green_white_innerfade btn_border_2px btn_medium \"><div class=\"subscribeIcon\"></div><span class=\"subscribeText\"><div id=\"SubscribeItemOptionAdd\" class=\"subscribeOption subscribe selected\">Finish</div></span></a>`""")
            except:
                pass

        if "steamcommunity.com" in driver.current_url and 'sharedfiles' not in driver.current_url:
            try:
                x = str(driver.execute_script("""return document.querySelector('a[class="header_installsteam_btn_content"]').href"""))
                if 'Game-K-Hack' not in x:            
                    execute_force("""document.querySelector('title').innerText = 'Wallpaper Downloader'""")
                    execute_force("""document.querySelector('link[rel="shortcut icon"]').href = 'https://cdn.discordapp.com/attachments/837345074877562892/840256392152481792/python.png'""")
                    execute_force("""document.querySelector('a[class="header_installsteam_btn_content"]').innerText = 'Installer DownPaper'""")
                    execute_force("""document.querySelector('a[class="header_installsteam_btn_content"]').href = 'https://github.com/Game-K-Hack'""")
                else:
                    pass
            except:
                pass
    except:
        try:
            driver.switch_to.window(driver.window_handles[0])
        except:
            break
quit()