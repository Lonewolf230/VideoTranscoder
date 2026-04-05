import subprocess
from multiprocessing import Process,set_start_method
import os
def transcode_video(input_path:str):
    ctx=__import__("multiprocessing").get_context("spawn")
    
    p1=ctx.Process(target=transcode_480,args=(input_path,))
    p2=ctx.Process(target=transcode_720,args=(input_path,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    errors=[]
    
    if p1.exitcode !=0:
        errors.append(f"480p transcoding failed with exit code {p1.exitcode}")
    if p2.exitcode !=0:
        errors.append(f"720p transcoding failed with exit code {p2.exitcode}")
    
    if errors:
        for suffix in ["_480p.mp4", "_720p.mp4"]:
            path = input_path.replace(".mp4", suffix)
            if os.path.exists(path):
                os.remove(path)
        raise RuntimeError("; ".join(errors))



def transcode_480(input_path:str):
    output_path=input_path.split(".")[0]+"_480p.mp4"
    command = [
        'ffmpeg',
        '-y',
        '-i', input_path,
        '-vf', 'scale=640:480',
        output_path
    ]
    try:
        subprocess.run(command, check=True)
        print("Transcoding to 480p completed successfully")
    except subprocess.CalledProcessError as e:
        print("Error during transcoding to 480p:", e)
        raise 
    
def transcode_720(input_path:str):
    output_path=input_path.split(".")[0]+"_720p.mp4"
    command = [
        'ffmpeg',
        '-y',
        '-i', input_path,
        '-vf', 'scale=1280:720',
        output_path
    ]
    try:
        subprocess.run(command, check=True)
        print("Transcoding to 720p completed successfully")
    except subprocess.CalledProcessError as e:
        print("Error during transcoding to 720p:", e)
        raise 