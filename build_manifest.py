import requests  
import json

# اسم الكتاب للتجربة
ITEM_ID = "book-90_202604"  

url = f"https://archive.org/metadata/{ITEM_ID}"  
resp = requests.get(url, timeout=30)  
data = resp.json()

server = data.get("server", "")  
dir_path = data.get("dir", "")  
workable = data.get("workable_servers", [server])  
files = data.get("files", [])

download_links = []  

for f in files:  
    name = f.get("name")  
    if not name:  
        continue  
        
    primary = f"https://{server}{dir_path}/{name}"  
    fallbacks = [f"https://{s}{dir_path}/{name}" for s in workable if s != server]  
    
    download_links.append({  
        "name": name,  
        "size": f.get("size"),  
        "md5": f.get("md5"),  
        "url": primary,  
        "fallbacks": fallbacks  
    })

output = {  
    "item_id": ITEM_ID,  
    "server": server,  
    "dir": dir_path,  
    "files": download_links  
}

# هنا النقطة الأهم: حفظ الملف باسم manifest.json حصراً
with open("manifest.json", "w", encoding="utf-8") as f:  
    json.dump(output, f, ensure_ascii=False, indent=2)

print("تم بنجاح! عدد الملفات المستخرجة:", len(download_links))
