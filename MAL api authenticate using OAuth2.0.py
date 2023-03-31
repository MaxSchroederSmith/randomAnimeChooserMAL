import requests, json, secrets, random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CLIENT_ID = 'cb9db6acd602ecdad6bcb8c42f262241'

auth_url = 'https://myanimelist.net/v1/oauth2/authorize'
access_token_url="http://localhost"

CODE_CHALLENGE = secrets.token_urlsafe(100)[:128]

#open chrome to get user to authenticate access

chrome_options = Options()
chrome_options.add_argument("user-data-dir=C:\\Users\\Max\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1") 
dr = webdriver.Chrome(options=chrome_options)

#dr = webdriver.Chrome()
dr.get("https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id="+CLIENT_ID+"+&code_challenge="+CODE_CHALLENGE)

#start server to capture authorisation code
import Server
authorisation_code = Server.authorisation_code

dr.quit() #once code has been done close chrome

#get access & refresh token
data = {
    "client_id" : CLIENT_ID,
    "grant_type" : "authorization_code",
    "code" : authorisation_code,
    "code_verifier" : CODE_CHALLENGE
}

tokens = requests.post("https://myanimelist.net/v1/oauth2/token",data=data)
access_token = tokens.json()['access_token']
refresh_token = tokens.json()['refresh_token']

#get total number of anime on the plan_to_watch list 
headers = {
    "Authorization" : "Bearer "+access_token
}

params = {
    "fields" : "anime_statistics"
    
}


anime_stats = requests.get("https://api.myanimelist.net/v2/users/@me", params=params, headers=headers)

if anime_stats.status_code !=200:
    print("shit went wrong trying to get anime stats")
anime_stats = anime_stats.json()
total_plan_to_watch = anime_stats["anime_statistics"]["num_items_plan_to_watch"]

anime_id = random.randint(0,total_plan_to_watch)
size_of_limit=100
params1 = {
    "status" : "plan_to_watch",
    "sort" : "list_updated_at",
    "fields" : "nsfw",
    "limit" : size_of_limit
}
url = "https://api.myanimelist.net/v2/users/@me/animelist"
anime_list = requests.get(url, params=params1, headers=headers)
while anime_id>=size_of_limit:
    url=anime_list.json()["paging"]["next"]
    anime_list = requests.get(url, params=params1, headers=headers)
    anime_id-=size_of_limit

if anime_list.status_code !=200:   
    print("Shit went wrong trying to page to the next part of the list!")


ani_id = anime_list.json()["data"][anime_id]["node"]["id"]
url = "https://api.myanimelist.net/v2/anime/"+str(ani_id)+"/my_list_status"

params2 = {
    "status" : "watching"
}
updating = requests.patch(url,data=params2,headers=headers)
if updating.status_code == 200:
    print("The anime you are now watching is: ")
    print(anime_list.json()["data"][anime_id]["node"]["title"])
else:
    print("shit really went wrong at the last step huh?!")
