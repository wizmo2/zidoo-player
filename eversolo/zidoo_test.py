from zidoorc import ZidooRC
import json
import logging

MAX = 5

logging.basicConfig(level=logging.DEBUG)

ip = input("Enter the devices IP address: ")
client = ZidooRC(ip)
client.connect()

print("get_power_status")
try:
    print(json.dumps(client.get_power_status(), indent=2))
except Exception as e:
    print(e)
print()      

print("get_playing_info")
try:
    print(json.dumps(client.get_playing_info(), indent=2))
except Exception as e:
    print(e)
print()      

print("generate_current_image_url")
try:
    print(json.dumps(client.generate_current_image_url(), indent=2))
except Exception as e:
    print(e)
print()   

print("get_app_list")
try:
    print(json.dumps(client.get_app_list(), indent=2))
except Exception as e:
    print(e)
print()      

print("get_device_list")
try:
    device_list = client.get_device_list();
    print(json.dumps(device_list, indent=2))
    for device in device_list:  
        print(device.get("name"))
        print(json.dumps(client.get_file_list(device.get("path")), indent=2))
except Exception as e:
    print(e)
print()      

print("get_music_list")
try:
    resp = client.get_music_list(max_count=MAX)
    print(json.dumps(resp, indent=2))
    music_list = resp.get("array")
    if len(music_list):
        print(music_list[0].get("album"))
        print("generate_image_url")
        print(json.dumps(client.generate_image_url(music_list[0].get("id"), "music"), indent=2))
except Exception as e:
    print(e)
print()      

print("get_movie_list")
try:
    resp = client.get_movie_list(max_count=MAX)
    print(json.dumps(resp, indent=2))
    movie_list = resp.get("data")
    if len(movie_list):
        print(movie_list[0].get("name"))
        print("generate_image_url")
        print(json.dumps(client.generate_image_url(movie_list[0].get("id"), "video"), indent=2))
except Exception as e:
    print(e)
print()      

print("get_video_playlist")
try:
    print(json.dumps(client.get_video_playlist(), indent=2))
except Exception as e:
    print(e)
print()  
print("get_music_playlist")
try:
    print(json.dumps(client.get_music_playlist(), indent=2))
except Exception as e:
    print(e)
print()  

print("get_volume_info")
try:
    print(json.dumps(client.get_volume_info(), indent=2))
except Exception as e:
    print(e)
print()   

resp = input("Press [0-4] to play music track: ")
if resp in "01234":
    try:
        client.play_music(music_list[int(resp)].get("id"))
    except Exception as e:
        print(e)
print()

resp = input("Press [0-4] to play movie: ")
if resp in "01234":
    try:
        client.play_movie(movie_list[int(resp)].get("id"))
    except Exception as e:
        print(e)
print()
print("FINISHED")
   
