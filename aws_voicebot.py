import asyncio  #Transcribe is async thats why we import this
import aiofile
import requests
#import sounddevice  #
import boto3
import datetime as dt
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
import speech_recognition as sr #use for saving file .wav
import subprocess
from gtts import gTTS
transc = ""

rec = sr.Recognizer()
with sr.Microphone() as source:
    print("Sprich: ")
    audio = rec.listen(source)        #listen to the source
    try:
        # write audio to a WAV file
        with open("microphone-results.wav", "wb") as f:
            f.write(audio.get_wav_data())
    except:
        print("Ich habe dich nicht verstanden") #voice not recognized

f.close()

class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        global transc
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
               transc = alt.transcript
                
async def basic_transcribe():
    global start_time
    start_time = dt.datetime.now()
    # Setup up our client with our chosen AWS region
    client = TranscribeStreamingClient(region="eu-central-1")
    settings = {
        'VocabularyName': 'FFMASRDominantWordVocab'
        }

    # Start transcription to generate our async stream
    stream = await client.start_stream_transcription(
        language_code="de-DE",
        media_sample_rate_hz=44100,
        media_encoding="pcm",
        vocabulary_name='FFMASRDominantWordVocab')

        # Instantiate our handler and start processing events
    
    async def write_chunks():
    # An example file can be found at tests/integration/assets/test.wav
    # NOTE: For pre-recorded files longer than 5 minutes, the sent audio
    # chunks should be rate limited to match the realtime bitrate of the
    # audio stream to avoid signing issues.
        async with aiofile.AIOFile('microphone-results.wav', 'rb') as afp:
            reader = aiofile.Reader(afp, chunk_size=1024 * 16)
            async for chunk in reader:
                await stream.input_stream.send_audio_event(audio_chunk=chunk)
        await stream.input_stream.end_stream()
    
    handler = MyEventHandler(stream.output_stream)
    print("no error")
    #print(stream.output_stream)
    #print(stream.response['TranscriptResultStream'])
    
    await asyncio.gather(write_chunks(), handler.handle_events())
    # for results in stream.output_stream:#.results.transcripts.transcript:
    #     for result in results:
    #         for alt in result.alternatives:
    #            transc = alt.transcript
    #            print(alt.transcript)

    
    

asyncio.run(basic_transcribe())  
# loop = asyncio.get_event_loop()
# tasks = [basic_transcribe()]
# loop.run_until_complete(asyncio.wait(tasks))
print("Last message: " + str(transc))
this_time = dt.datetime.now()
that_time = this_time - start_time
print("--- %s seconds ---" % (that_time))

r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": transc.replace(".","").replace("?","").replace(",","")})
for i in r.json():
    bot_message = i['text']
    print(f"{bot_message}")

language = 'de' #Language of spoken text
print(bot_message)
myobj = gTTS(text=bot_message, lang=language)
myobj.save("welcome.mp3")       #response
print('saved')
subprocess.call(['C:\\Program Files\\VideoLAN\\VLC\\vlc.exe',  '--rate=1.75',r"C:\Users\rene\shoppinglist5\welcome.mp3", '--play-and-exit'])
while bot_message != "Bye" or bot_message!='thanks':
    with sr.Microphone() as source:
        print("Sprich neu: ")
        audio = rec.listen(source)        #listen to the source
        try:
            # write audio to a WAV file
            with open("microphone-results.wav", "wb") as f:
                f.write(audio.get_wav_data())
            print("saved new audiofile")           
        except:
            print("Ich habe dich nicht verstanden") #voice not recognized
            continue

    f.close()        
    asyncio.run(basic_transcribe())
    print("Last message: " + str(transc))
    this_time = dt.datetime.now()
    that_time = this_time - start_time
    print("--- %s seconds ---" % (that_time))
    if len(transc) ==0:
        continue
    print("Nachricht wird übermittelt")
    print(transc)
    r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": transc.replace(".","").replace("?","").replace(",","")})
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



    

# loop = asyncio.get_event_loop()
# loop.run_until_complete(basic_transcribe())
# loop.close()
# async def mic_stream():
#     loop = asyncio.get_event_loop()
#     input_queue = asyncio.Queue()

#     def callback(indata, frame_count, time_info, status):
#         loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

#     #configure for RWU settings 
#     #https://docs.aws.amazon.com/transcribe/latest/dg/streaming.html
#     stream = sounddevice.RawInputStream(
#         channels=1,
#         samplerate=16000,
#         callback=callback,
#         blocksize=1024 * 2,
#         dtype="int16"
#     )
    # #Initiate the audio stream and asynchronously yield the audio chunks as they become available
    # with stream:
    #     while True:
    #         indata, status = await input_queue.get()
    #         yield indata, status

# async def write_chunks():
#     # An example file can be found at tests/integration/assets/test.wav
#     async with aiofile.AIOFile('tests/integration/assets/test.wav', 'rb') as afp:
#         reader = aiofile.Reader(afp, chunk_size=1024 * 16)
#         async for chunk in reader:
#             await stream.input_stream.send_audio_event(audio_chunk=chunk)
#     await stream.input_stream.end_stream()

# async def basic_transcribe():
#     client = TranscribeStreamingClient(region="eu-central-1")
    
#     #Start transcription, generate async stream
#     stream = await client.start_stream_transcription(
#         language_code="de-DE",
#         media_sample_rate_hz=16000,
#         media_encoding="pcm",
#         vocabulary_name="FFMASRDominantWordVocab"    
#     )

#     handler = MyEventHandler(stream.output_stream)
#     await asyncio.gather(write_chunks(stream), handler.handle_events())



# loop = asyncio.get_event_loop()
# loop.run_until_complete(basic_transcribe())
# loop.close()