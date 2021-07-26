'''
Google Video Intelligence API utility  scripts for analysing videos.
Pass in a Google Storage input folder/file and Google Storage output folder/file

'''


from google.cloud import videointelligence
from google.cloud import storage

import argparse


def is_json(gs_path):
    return '.' in  gs_path

def is_video(gs_path):
    return '.' in  gs_path

def analyze_video(gcs_uri, output_uri, service_key):

    # gcs_uri = "gs://YOUR-BUCKET/video folder"
    # gcs_output_folder = "gs://YOUR-BUCKET/outputs"
    # service_key = "your_local_service_account_file.json"

    video_client = videointelligence.VideoIntelligenceServiceClient.from_service_account_file(service_key)

    features = [
        videointelligence.Feature.OBJECT_TRACKING,
        videointelligence.Feature.LABEL_DETECTION,
        videointelligence.Feature.SHOT_CHANGE_DETECTION,
        videointelligence.Feature.SPEECH_TRANSCRIPTION,
        videointelligence.Feature.LOGO_RECOGNITION,
        videointelligence.Feature.EXPLICIT_CONTENT_DETECTION,
        videointelligence.Feature.TEXT_DETECTION,
        videointelligence.Feature.FACE_DETECTION,
        videointelligence.Feature.PERSON_DETECTION
    ]

    transcript_config = videointelligence.SpeechTranscriptionConfig(
        language_code="en-US", enable_automatic_punctuation=True
    )

    person_config = videointelligence.PersonDetectionConfig(
        include_bounding_boxes=True,
        include_attributes=False,
        include_pose_landmarks=True,
    )

    face_config = videointelligence.FaceDetectionConfig(
        include_bounding_boxes=True, include_attributes=True
    )


    video_context = videointelligence.VideoContext(
        speech_transcription_config=transcript_config,
        person_detection_config=person_config,
        face_detection_config=face_config)

    operation = video_client.annotate_video(
        request={"features": features,
                "input_uri": gcs_uri,
                "output_uri": output_uri,
                "video_context": video_context}
    )

    print("\nProcessing video...", operation)


parser = argparse.ArgumentParser()
parser.add_argument("gcs_input", help="gcs file or folder of videos to analyse")
parser.add_argument("gcs_output", help="gcs folder of the output files")
parser.add_argument("service_key", help="file name of .json service account key")
args = parser.parse_args()
print('input folder', args.gcs_input)
print('output folder',args.gcs_output)


storage_client = storage.Client()

# code for analysing a single input file
if is_video(args.gcs_input):
    print('is just single file', args.gcs_input)
    if is_json(args.gcs_output):
        print('specific output file specified', args.gcs_output)
        analyze_video(args.gcs_input, args.gcs_output, args.service_key)
    else:
        file_name =  args.gcs_input.split('/')[-1].split('.')[0]
        gcs_output = args.gcs_output if args.gcs_output[-1] != '/' else args.gcs_output[:-1]
        output_uri = gcs_output + '/' + file_name + '.json'
        print('output folder specified', args.gcs_output )
        analyze_video(args.gcs_input, output_uri, args.service_key)
    quit()

# code for analysing a folder of files
gcs_input = args.gcs_input.replace('gs://','')
gcs_output = args.gcs_output if args.gcs_output[-1] != '/' else args.gcs_output[:-1]

parts = gcs_input.split('/')
bucket_name = parts[0]
prefix = '/'.join(parts[1:]) if len(parts) > 1 else ''

blobs = storage_client.list_blobs(bucket_name, prefix=prefix)

for blob in list(blobs):
    path = 'gs://' + bucket_name + '/' + blob.name
    print('found file...', path)

    file_name =  blob.name.split('/')[-1].split('.')[0]
    output_uri = gcs_output + '/' + file_name + '.json'
    
    if is_video(path):
        analyze_video(path, output_uri, args.service_key)
    




