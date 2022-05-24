import time
import boto3
counter = 0
settings = {
        'VocabularyName': 'FFMASRDominantWordVocab'
        }
transcribe = boto3.client('transcribe')
job_name = "job-name2"
job_uri = "s3://log-delivery-2022/microphone-results.wav"
transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': job_uri},
    MediaFormat='wav',
    LanguageCode='de-DE',
    Settings = settings)
while True:
    status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    counter += 2
    print("Not ready yet..." + str(counter))
    time.sleep(2)
print(status)