import requests  
import json

# 1. اسم الكتاب الذي نبحث عنه في أرشيف
ITEM_ID = "book-90_202604"  

# 2. نطلب من الموقع إعطاءنا بطاقة تعريف الكتاب (Metadata)
url = f"https://archive.org/metadata/{ITEM_ID}"  
resp = requests.get(url, timeout=30)  
data = resp.json()

# 3. نستخرج الخوادم والمسارات من البطاقة
server = data.get("server", "")  
dir_path = data.get("dir", "")  
workable = data.get("workable_servers", [server])  
files = data.get("files", [])

# 4. نجهز قائمة فارغة لنضع فيها الروابط المباشرة التي سنصنعها
download_links = []  

# 5. نمر على كل ملف داخل الكتاب (لأن الكتاب قد يحتوي عدة ملفات)
for f in files:  
    name = f.get("name")  
    
    # إذا لم يكن هناك اسم للملف، نتجاهله
    if not name:  
        continue  
        
    # نصنع الرابط المباشر الأساسي بدمج الخادم + المسار + اسم الملف
    primary = f"https://{server}{dir_path}/{name}"  
    
    # نصنع روابط احتياطية من الخوادم البديلة (إذا فشل الأول، يعمل الثاني)
    fallbacks = [f"https://{s}{dir_path}/{name}" for s in workable if s != server]  
    
    # نجمع المعلومات ونضعها في القائمة
    download_links.append({  
        "name": name,  
        "size": f.get("size"),  
        "md5": f.get("md5"),  
        "url": primary,  
        "fallbacks": fallbacks  
    })

# 6. نرتب كل شيء في شكل خريطة نهائية أنيقة
output = {  
    "item_id": ITEM_ID,  
    "server": server,  
    "dir": dir_path,  
    "files": download_links  
}

# 7. نحفظ هذه الخريطة في ملف اسمه JSON ليقرأه تطبيق الأندرويد لاحقاً
with open(f"{ITEM_ID}_links.json", "w", encoding="utf-8") as f:  
    json.dump(output, f, ensure_ascii=False, indent=2)

print("تم إنشاء الملف بنجاح! عدد الملفات:", len(download_links))
