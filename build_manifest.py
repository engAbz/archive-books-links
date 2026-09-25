import requests
import json

# يمكنك تغيير هذا المعرف لاحقاً أو جعله متغيراً ديناميكياً
ITEM_ID = "book-90_202604"  

url = f"https://archive.org/metadata/{ITEM_ID}"  
resp = requests.get(url, timeout=30)  
data = resp.json()

# -- معالجة الملاحظة الثالثة: بناء درع السيرفرات البديلة --
primary_server = data.get("server", "")  
dir_path = data.get("dir", "")  

# نستخدم Set لمنع التكرار نهائياً
fallback_servers = set()

# 1. جلب السيرفرات المتاحة من القائمة إن وجدت
workable = data.get("workable_servers", [])
if isinstance(workable, list):
    for s in workable:
        fallback_servers.add(s)
elif isinstance(workable, str):
    fallback_servers.add(workable)

# 2. جلب d1 و d2 إن وجدت في البيانات
if data.get("d1"): fallback_servers.add(data.get("d1"))
if data.get("d2"): fallback_servers.add(data.get("d2"))

# 3. إزالة السيرفر الرئيسي من البدائل كي لا نصنع حلقة مفرغة
if primary_server in fallback_servers:
    fallback_servers.remove(primary_server)


files = data.get("files", [])
download_links = []  

# -- معالجة الملاحظة الثانية: فلترة الصيغ المتعددة --
# هنا نحدد الصيغ المطلوبة. يمكنك إضافة أي صيغة أخرى مستقبلاً
allowed_extensions = (".db", ".pdf", ".epub")

for f in files:  
    name = f.get("name")  
    if not name:  
        continue  
        
    # الشرط: هل ينتهي اسم الملف بإحدى الصيغ المسموحة؟ إذا لم يكن كذلك، تخطاه.
    if not name.lower().endswith(allowed_extensions):
        continue
        
    primary_url = f"https://{primary_server}{dir_path}/{name}"  
    
    # بناء روابط السيرفرات البديلة للملف الحالي
    file_fallbacks = []
    for server_name in fallback_servers:
        file_fallbacks.append(f"https://{server_name}{dir_path}/{name}")
    
    download_links.append({  
        "name": name,  
        "size": f.get("size"),  
        "md5": f.get("md5"),  
        "url": primary_url,  
        "fallbacks": file_fallbacks  
    })

# تجميع الناتج النهائي
output = {  
    "item_id": ITEM_ID,  
    "server": primary_server,  
    "dir": dir_path,  
    "files": download_links  
}

# حفظ الملف. استخدمنا ensure_ascii=False لدعم أي نصوص عربية في أسماء الكتب
with open("manifest.json", "w", encoding="utf-8") as file:  
    json.dump(output, file, ensure_ascii=False, indent=2)

print("تمت العملية بنجاح! عدد الملفات المفلترة والمحمية:", len(download_links))
