import sounddevice as sd
from scipy.io.wavfile import write
import aiofile
import subprocess
import time
import boto3
import pandas as pd
import asyncio  #Transcribe is async thats why we import this
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                print(alt.transcript)

def check_job_name(job_name):
  job_verification = True
  # all the transcriptions
  existed_jobs = amazon_transcribe.list_transcription_jobs()
  for job in existed_jobs['TranscriptionJobSummaries']:
    if job_name == job['TranscriptionJobName']:
      job_verification = False
      break
    if job_verification == False:
      command = input(job_name + " has existed. \nDo you want to override the existed job (Y/N): ")    if command.lower() == "y" or command.lower() == "yes":                transcribe.delete_transcription_job(TranscriptionJobName=job_name)
    elif command.lower() == "n" or command.lower() == "no":      
       job_name = input("Insert new job name? ")      
       check_job_name(job_name)
    else:
      print("Input can only be (Y/N)")
      command = input(job_name + " has existed. \nDo you want to override the existed job (Y/N): ")
    
  return job_name

def amazon_transcribe(audio_file_name):
  job_uri = # your S3 access link
  # Usually, I put like this to automate the process with the file name
  # "s3://bucket_name" + audio_file_name  
  # Usually, file names have spaces and have the file extension like .mp3
  # we take only a file name and delete all the space to name the job
  job_name = (audio_file_name.split('.')[0]).replace(" ", "")  
  # file format  
  file_format = audio_file_name.split('.')[1]
  
  # check if name is taken or not
  job_name = check_job_name(job_name)
  amazon_transcribe.start_transcription_job(
      TranscriptionJobName=job_name,
      Media={'MediaFileUri': job_uri},
      MediaFormat = file_format,
      LanguageCode='de-DE')
  
  while True:
    result = amazon_transcribe.get_transcription_job(TranscriptionJobName=job_name)
    if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    time.sleep(5)
    if result['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
        data = pd.read_json(result['TranscriptionJob']['Transcript']['TranscriptFileUri'])
  return data['results'][1][0]['transcript']


    # async for chunk, status in mic_stream():
    #     await stream.input_stream.send_audio_event(audio_chunk=chunk)
    # await stream.input_stream.end_stream

# fs = 16000  # Sample rate
# seconds = 8  # Duration of recording

# myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
# sd.wait()  # Wait until recording is finished
# write('output.wav', fs, myrecording)  # Save as WAV file 
async def basic_transcribe():
    client = TranscribeStreamingClient(region="eu-central-1")
    print("working central")
    stream = await client.start_stream_transcription(
        language_code="de-DE",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
        vocabulary_name="FFMASRDominantWordVocab"    
    )
    handler = MyEventHandler(stream.output_stream)
    print("handler")
    await asyncio.gather(write_chunks(stream), handler.handle_events())


subprocess.call(['C:\\Program Files\\VideoLAN\\VLC\\vlc.exe',  '--rate=1.75',r"C:\Users\rene\shoppinglist5\output.wav", '--play-and-exit'])
loop = asyncio.get_event_loop()
loop.run_until_complete(basic_transcribe())
loop.close()