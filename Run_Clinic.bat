@echo off
:: تشغيل حاويات دوكر في الخلفية بصمت (تجنباً لأي توقف سابق)
docker start n8n whatsapp-server >nul 2>&1

:: استخدام pythonw لتشغيل الواجهات بدون ظهور الشاشة السوداء
start pythonw clinic.py
start pythonw display.py

exit