import speech_recognition as sr
import time
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Sprich: ")
    audio = r.listen(source)        #listen to the source
    try:
        start_time = time.time()
        print(type(audio))
        # write audio to a WAV file
        with open("microphone-results.wav", "wb") as f:
            f.write(audio.get_wav_data())
        text = ""#r.recognize_google(audio, language="de-DE")    #use recognizer to convert our audio into text
        print("Du sagtest: {}".format(text))
        print("--- %s seconds ---" % (time.time() - start_time))
    except:
        print("Ich habe dich nicht verstanden") #voice not recognized
    # try:
    #     text = r.recognize_ibm(audio)
    #     print("IBM understood: {}".format(text))
    #     print("--- %s seconds ---" % (time.time() - start_time))
    # except:
    #     print("Ich habe dich nicht verstanden") #voice not recognized





# myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
# sd.wait()  # Wait until recording is finished
# write('output.wav', fs, myrecording)  # Save as WAV file 