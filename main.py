from pytubefix import YouTube
from pytubefix import Search
import humanize
import os
import requests
import subprocess
from random import randint
import urllib.request

destination_foulder = os.path.join(".", "Destination")
os.makedirs(destination_foulder, exist_ok=True)

random_name = str(randint(100, 9999)) + '.jpg'
thumb_path = os.path.join(destination_foulder, random_name)


def check_valid_url(input: str):
    input = input.strip()
    prefixes = ("https:", "http:", "youtube.com", "www.", "youtu.be")
    domains = ["youtube.com", "youtu.be"]
    allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    rule_out = ["shorts", "live", "embed", "playlist", "@", "music"]
    temp = []

    # make sure that this link is a youtube domain valid 
    if input.startswith(prefixes) and any(d in input for d in domains):
        # rule out different youtube services
        if any(service in input for service in rule_out):
            return False, 2, "Invalid: Is Not a Video" #TODO upcoming feature potential
        
        # old format handeling
        elif "/v/" in input:
            temp = input.split("/v/")
            id = temp[1]
        
        else:
            
            # unfamalier format handeling
            if "app=desktop&" in input:
                input = input.replace("watch?app=desktop&v=", "watch?v=")

            temp = input.split('/')
            for part in temp: 
                if any(p in part for p in prefixes) or "" == part:
                    continue
                else:
                    id_unfileterd = part
                    break

            if "watch?v=" in id_unfileterd :
                id = id_unfileterd[8:19]
            else:
                id = id_unfileterd[:11]

        for c in id:
            if c not in allowed_chars:
                return False, 2, "Invalid: Corrupt Video ID"

        return True, id

    else:
        return False, 1
    

def  main_search():
    while True:
        search_input = input("Search Words / URL: ")
        result = check_valid_url(search_input)
        # in case it's a true link
        if result[0] == True:
            url = f"https://youtube.com/watch?v={result[1]}"
            return url
        # in case it's a link but the user messed it up
        else:
            if result[1] == 2:
                print("Please Retype the URL")
                print(f"Details: {result[2]}")
                print("\n ------------------")
            # the user does not intend to type a link
            else:
                output = Search(search_input).videos[:10]
                if not output:
                    print("No search results found. Please try again.")
                    continue
                sorted_output = sorted(
                    output,
                    key=lambda x: x.views,
                    reverse=True
                )
                while True:
                    n = input("how many top search results do you want (keep blank for first result) ? ")
                    if n == '':
                        return sorted_output[0].watch_url
                    if not n.isdigit():
                        print("Invalid Input: Numbers Only Allowed")
                        continue
                    n_int = int(n)
                    if n_int <= 0:
                        print("Invalid Input: number must be more than 0")
                        continue
                    elif n_int > 10 :
                        print(f"tf are you gonna do with {n_int} results :/")
                        print("Please Enter Anoter Number")
                        continue
                    organize_num = 0
                    for i in sorted_output[:n_int]:
                        organize_num += 1
                        clean_title = i.title.replace("|", "-")
                        clean_date = str(i.publish_date).split(" ")
                        print(f"{organize_num}. {clean_title} | {i.author} | {humanize.intword(i.views)} | {clean_date[0]} ")
                    try:
                        choice = int(input("Which one do you choose (number): "))
                        if 1 <= choice <= n_int:
                            return sorted_output[choice - 1].watch_url
                        else:
                            print("Invalid choice: out of range.")
                    except ValueError:
                        print("Invalid Input: Please enter a number.")


def thumbnail_img(url):
    id = check_valid_url(url)
    thumbnial_link = f"https://img.youtube.com/vi/{id[1]}/hqdefault.jpg"

    rec = urllib.request.Request(
        thumbnial_link,
        headers={'User-Agent': 'Mozilla/5.0'}
    )

    with urllib.request.urlopen(rec) as response:
        with open(thumb_path, "wb") as f:
            f.write(response.read())

    
def attach_thumbnail(file_path, thumb_path):
    if not os.path.exists(thumb_path):
        print("Thumbnail file not found, skipping.")
        return
    
    ext = os.path.splitext(file_path)[1].lower()
    temp_output = file_path.replace(ext, f"_temp{ext}")
    
    cmd = ['ffmpeg', '-i', file_path, '-i', thumb_path]
    
    if ext == '.mp3':
        cmd += ['-map', '0:0', '-map', '1:0', '-c', 'copy', '-id3v2_version', '3', 
                '-metadata:s:v', 'title="Album cover"', '-metadata:s:v', 'comment="Cover (front)"']
    elif ext in ['.mp4', '.m4a']:
        cmd += ['-map', '0:a', '-map', '1:v', '-c', 'copy', '-disposition:v:0', 'attached_pic']
    elif ext in ['.webm', '.opus']:
        cmd += ['-map', '0', '-map', '1', '-c', 'copy', '-metadata:s:v', 'title="Album cover"']
    else:
        print(f"Unknown extension {ext}, skipping thumbnail link.")
        return
    
    cmd += ['-y', temp_output]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        os.replace(temp_output, file_path)
        print("Thumbnail linked successfully!")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed: {e.stderr.decode()}")
        if os.path.exists(temp_output):
            os.remove(temp_output)  # Clean up temp file on failure
    finally:
        if os.path.exists(thumb_path):
            os.remove(thumb_path)


def download(url):
    yt = YouTube(url)
    
    thumbnail_img(url)

    while True:
        user_choice = input("Do you want a video or an audio (A/V)? ").upper()
        if user_choice not in ['A', 'V']:
            print("Invalid Input: Please Try Again")
        else:
            break
    
    if user_choice == "V":
        is_video = True
        streams = yt.streams.filter(progressive=True).order_by("resolution").desc()
    else:
        is_video = False
        streams = yt.streams.filter(only_audio=True).order_by("abr").desc()

    if not streams:
        print("No streams found for this category.")
        return

    print(f"\n--- Available Quality for: {yt.title} ---")
    for s in streams:
        quality = s.resolution if is_video else s.abr
        extra = f"FPS: {s.fps}" if is_video else f"Codec: {s.audio_codec}"
        
        print(f"ITAG: {s.itag} | {quality} | {s.mime_type} | {extra}")

    try:
        final_choice = input("\nEnter ITAG number to download: ")
        if final_choice == "":
            stream = streams.first()
        else:
            int(final_choice)
            stream = streams.get_by_itag(final_choice)
        
        print(f"Downloading: {yt.title}...")

        file_path = stream.download(output_path=destination_foulder)
        print(f"Success! Saved to: {file_path}")  
    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        print("Processing file with FFmpeg...")
        attach_thumbnail(file_path, thumb_path) 
        # link_thumbnail should handle the 'temp' file renaming internally 
    finally:
        # This block runs NO MATTER WHAT (success or error)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
            print("Cleaned up temporary thumbnail.")

if __name__ == "__main__":
    download(main_search())

