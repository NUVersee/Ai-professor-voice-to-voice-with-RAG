import requests
url = "https://ayyyhaga-prof2-ayhaga.hf.space/text-to-text"
r = requests.post(url, json={"question":"what is the student activities in nile university?"})
print(r.json())
