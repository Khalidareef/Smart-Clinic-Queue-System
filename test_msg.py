import requests

print("جاري إرسال الرسالة التجريبية...")

# 1. الحصول على التصريح (التوكن)
token_url = "http://localhost:8080/api/clinic/ClinicKey123/generate-token"
token = requests.post(token_url).json().get("token")

# 2. إعداد الرسالة
send_url = "http://localhost:8080/api/clinic/send-message"
headers = {"Authorization": f"Bearer {token}"}

# رقم الهاتف مسبوقاً بمفتاح مصر (20) وبدون أي مسافات أو علامة +
phone_number = "201115098914" 

payload = {
    "phone": phone_number,
    "isGroup": False,
    "message": "أهلاً بك يا مهندس خالد! هذه رسالة تجريبية من نظام العيادة الذكي عبر الواتساب. 🎉"
}

# 3. إرسال الطلب
response = requests.post(send_url, headers=headers, json=payload)

if response.ok:
    print("✅ تم إرسال الرسالة بنجاح! تفقد هاتفك.")
else:
    print("❌ فشل الإرسال، رد السيرفر:")
    print(response.text)