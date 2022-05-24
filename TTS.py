import subprocess
from gtts import gTTS
mytext = 'Herzlich willkommen' #Text for Audio
language = 'de' #Language of spoken text

myobj = gTTS(text=mytext, lang=language)
myobj.save("welcome.mp3")
subprocess.call(['C:\\Program Files\\VideoLAN\\VLC\\vlc.exe',  '--rate=1.5',r"C:\Users\rene\shoppinglist5\welcome.mp3", '--play-and-exit'])