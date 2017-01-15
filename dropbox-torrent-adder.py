from sys import argv
from threading import Timer
from pushbullet import Pushbullet
import config
import dropbox
import os
import transmissionrpc
import smtplib

os.chdir(config.dir)

def file_check():
    Timer(30, file_check).start()
    dbx = dropbox.Dropbox(config.dropbox_api_key)
    dbx.users_get_current_account()
    tc = transmissionrpc.Client()

    for entry in dbx.files_list_folder('').entries:
        if not os.path.isfile("./" + entry.name) and entry.name.endswith('.torrent'):
            metadata, f = dbx.files_download("/" + entry.name)
            out = open(entry.name, 'wb+')
            out.write(f.content)
            out.close()
            file = os.path.abspath(entry.name)
            tc.add_torrent(file)
            print("Added" + entry.name)
            notify("Torrent " + entry.name + " was added to transmission")

def notify(notify_text):
    if config.notify_method == "mail":
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(config.email, config.email_password)
        server.sendmail(config.email, config.notify_email, notify_text)
        server.quit()
    elif config.notify_method == "pushbullet":
        pb = Pushbullet(config.pushbullet_api_key)
        push = pb.push_note("New torrent added!", notify_text)

file_check()
