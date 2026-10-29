import requests
import webbrowser

print("جاري تهيئة سيرفر الواتساب واستخراج رمز الاستجابة (QR)... يرجى الانتظار...")

token_url = "http://localhost:8080/api/clinic/ClinicKey123/generate-token"
response_token = requests.post(token_url)

if not response_token.ok:
    print("❌ فشل الحصول على التوكن!")
    exit()

token = response_token.json().get("token")

session_url = "http://localhost:8080/api/clinic/start-session"
headers = {"Authorization": f"Bearer {token}"}
payload = {"waitQrCode": True}

response_session = requests.post(session_url, headers=headers, json=payload)

if not response_session.ok:
    print("❌ فشل بدء الجلسة!")
    exit()

session_res = response_session.json()

if "qrcode" in session_res and session_res["qrcode"]:
    qr_data = session_res["qrcode"]
    
    # إصلاح صيغة الصورة لكي تظهر في المتصفح
    if not qr_data.startswith("data:image"):
         # أحياناً يحتوي النص على بادئة مختلفة مثل 'data:image/png;base64,'
         # إذا لم تكن موجودة نضيفها
         # في wppconnect غالبا تأتي هكذا مباشرة ولكن للتأكد:
         if "," in qr_data:
             pass # الصيغة سليمة
         else:
             qr_data = f"data:image/png;base64,{qr_data}"

    html = f'''
    <html>
        <body style="text-align:center; font-family:sans-serif; margin-top:50px;">
            <h2>امسح الكود بهاتف العيادة لربط الواتساب</h2>
            <img src="{qr_data}" style="box-shadow: 0 0 10px rgba(0,0,0,0.1); padding: 20px; border-radius: 10px; max-width: 400px;">
            <br><p>WPPConnect Server</p>
        </body>
    </html>
    '''
    with open("qr.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    webbrowser.open("qr.html")
    print("✅ تم فتح المتصفح! قم بمسح الكود الآن.")
else:
    print("⚠️ لم يتم العثور على الكود:")
    print(session_res)