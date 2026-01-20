from pytubefix import YouTube
from pytubefix import Search
import humanize

def search_fun():
    search_input = input("Search: ")
    output = Search(search_input)
    n = int(input("how many top search results do you want ? (1 - 10) "))

    organize_num = 0
    for i in output.videos[:n]:
        organize_num += 1
        clean_title = i.title.replace("|", "-")
        clean_date = str(i.publish_date).split(" ")
        print(f"{organize_num}. {clean_title} | {i.author} | {humanize.intword(i.views)} | {clean_date[0]} | {i.watch_url}")
    choice = int(input("Which one did you choose (number): "))
    return output.videos[choice - 1].watch_url

def download(url):
    yt = YouTube(url)
    user_choice = input("Do you want a video or an audio (A/V)? ").upper()
    
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
        final_choice = int(input("\nEnter ITAG number to download: "))
        stream = streams.get_by_itag(final_choice)
        
        print(f"Downloading: {yt.title}...")

        file_path = stream.download(output_path="./destination")
        print(f"Success! Saved to: {file_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    

download(search_fun())