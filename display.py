import sys
import json
import os
import winsound
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

class WebWaitingRoomDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.last_data_str = ""
        self.last_number = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("شاشة العرض الذكية - VIP")
        self.showFullScreen()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QWebEngineView()
        
        # التأكد من ربط الشاشة بملف التصميم الجديد
        html_path = os.path.abspath("clinic_waiting_modern.html")
        self.browser.setUrl(QUrl.fromLocalFile(html_path))
        layout.addWidget(self.browser)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_updates)
        self.update_timer.start(1000)

    def check_updates(self):
        if os.path.exists("current.json"):
            try:
                with open("current.json", "r", encoding="utf-8") as f:
                    raw_data = f.read()
                
                if raw_data != self.last_data_str:
                    self.last_data_str = raw_data
                    data = json.loads(raw_data)
                    
                    current_number = data.get("queue_number", "")
                    waiting_list = data.get("waiting_list", [])
                    
                    # إصدار صوت فقط إذا تغير الرقم ولم يكن فارغاً
                    if current_number != self.last_number and self.last_number is not None and current_number != "":
                        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                    
                    self.last_number = current_number

                    # تحويل القائمة لصيغة نصية لتقرأها جافاسكريبت
                    waiting_list_json = json.dumps(waiting_list, ensure_ascii=False)
                    
                    # حقن البيانات الحية في التصميم الحديث
                    js_code = f"""
                        document.body.classList.add('kiosk');
                        state.current = '{current_number}';
                        state.queue = {waiting_list_json};
                        render();
                    """
                    self.browser.page().runJavaScript(js_code)
            except Exception as e:
                pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WebWaitingRoomDisplay()
    window.show()
    sys.exit(app.exec_())