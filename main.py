from pytubefix import YouTube
from pytubefix import Search
import humanize

def search_fun():
    search_input = input("Search: ")
    output = Search(search_input)
    n = int(input("how many top search results do you want ? (1 - 10)"))

    organize_num = 0
    for i in output.videos[:n]:
        organize_num += 1
        print(f"{organize_num}. {i.title.replace("|", "-")} | {i.author} | {humanize.intword(i.views)} | {i.publish_date} | {i.watch_url}")
    choice = int(input("Which one did you choose (number): "))
    return output.videos[choice - 1].watch_url

