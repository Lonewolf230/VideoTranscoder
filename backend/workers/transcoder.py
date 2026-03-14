import subprocess
from multiprocessing import Process

def transcode_video(input_path:str):
    
    p1=Process(target=transcode_480,args=(input_path,))
    p2=Process(target=transcode_720,args=(input_path,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()



def transcode_480(input_path:str):
    output_path=input_path.split(".")[0]+"_480p.mp4"
    command = [
        'ffmpeg',
        '-i', input_path,
        '-vf', 'scale=640:480',
        output_path
    ]
    subprocess.run(command, check=True)
    print("Transcoding to 480p completed successfully")
    
def transcode_720(input_path:str):
    output_path=input_path.split(".")[0]+"_720p.mp4"
    command = [
        'ffmpeg',
        '-i', input_path,
        '-vf', 'scale=1280:720',
        output_path
    ]
    subprocess.run(command, check=True)
    print("Transcoding to 720p completed successfully")