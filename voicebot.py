import requests
import azure.cognitiveservices.speech as speechsdk
import subprocess
from gtts import gTTS
import time
bot_message = ""
message = ""
# realized with azure so far
def recognize_from_microphone(message: message):
    subscriptionKey = "79f56803b51341cb91f570df5fdf80d7"
    serviceRegion = "westeurope"
    speech_config = speechsdk.SpeechConfig(subscription=subscriptionKey, region=serviceRegion)
    speech_config.speech_recognition_language="de-DE"
    message = ""
    #To recognize speech from an audio file, use `filename` instead of `use_default_microphone`:
    #audio_config = speechsdk.audio.AudioConfig(filename="YourAudioFile.wav")
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Sprich etwas.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Eingabe: {}".format(speech_recognition_result.text))
        message = speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    
    return message



r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": "Hello"})
for i in r.json():
        bot_message = i['text']
        print(f"{bot_message}")

language = 'de' #Language of spoken text
print(bot_message)
myobj = gTTS(text=bot_message, lang=language)
myobj.save("welcome.mp3")
print('saved')
subprocess.call(['C:\\Program Files\\VideoLAN\\VLC\\vlc.exe',  '--rate=1.75',r"C:\Users\rene\shoppinglist5\welcome.mp3", '--play-and-exit'])
while bot_message != "Bye" or bot_message!='thanks':
    message = recognize_from_microphone(message)
    # r = sr.Recognizer()
    # with sr.Microphone() as source:
    #     print("Sprich etwas: ")
    #     audio = r.listen(source)
    #     try: 
    #         message = r.recognize_google(audio, language="de-DE")
    #         print("Eingabe: {}".format(message))
    #         print("--- %s seconds ---" % (time.time() - start_time))
    #     except:
    #         print("Stimme wurde nicht erkannt")
    if len(message)==0:
        continue
    print("Nachricht wir übermittelt...")
    print(message.replace(".",""))
    message = message.replace(".","")
    r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": message})
    print("Bot says, ", end=' ')
    for i in r.json():
        bot_message = i['text']
        print(f"{bot_message}")
    language = 'de' #Language of spoken text
    print(bot_message)
    myobj = gTTS(text=bot_message, lang=language)
    myobj.save("welcome.mp3")
    print("saved")
    subprocess.call(['C:\\Program Files\\VideoLAN\\VLC\\vlc.exe',  '--rate=1.75',r"C:\Users\rene\shoppinglist5\welcome.mp3", '--play-and-exit'])


