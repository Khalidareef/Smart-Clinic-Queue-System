import sys
import requests
import mysql.connector
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView)

class ClinicApp(QWidget):
    def __init__(self):
        super().__init__()
        # رابط n8n المبدئي (سنقوم بإعداده في الخطوة القادمة)
        self.webhook_url = "http://localhost:5678/webhook/patient-event"
        self.init_db()
        self.init_ui()
        self.load_data()

    def init_db(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678", # ضع كلمة المرور الخاصة بك هنا
                database="clinic_db"
            )
            self.cursor = self.db.cursor(dictionary=True)
        except Exception as e:
            QMessageBox.critical(self, "خطأ في الاتصال", f"تأكد من تشغيل MySQL: {e}")
            sys.exit()

    def init_ui(self):
        self.setWindowTitle("نظام إدارة العيادة - واجهة السكرتارية")
        self.resize(650, 450)
        # تصميم عصري للبرنامج
        # تصميم عصري واحترافي (Modern Medical UI)
        self.setStyleSheet("""
            /* خلفية البرنامج العامة */
            QWidget {
                background-color: #F0F4F8;
                font-family: 'Segoe UI', Tahoma, sans-serif;
                font-size: 15px;
                color: #2D3748;
            }
            
            /* الحقول النصية (Inputs) */
            QLineEdit {
                padding: 12px;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #4299E1;
                background-color: #F7FAFC;
            }
            
            /* الأزرار (Buttons) */
            QPushButton {
                padding: 14px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                color: white;
                border: none;
            }
            
            /* زر الإضافة (أخضر زاهي) */
            QPushButton#add_btn {
                background-color: #48BB78;
            }
            QPushButton#add_btn:hover {
                background-color: #38A169;
            }
            QPushButton#add_btn:pressed {
                background-color: #2F855A;
            }
            
            /* زر المريض التالي (أزرق طبي) */
            QPushButton#next_btn {
                background-color: #3182CE;
            }
            QPushButton#next_btn:hover {
                background-color: #2B6CB0;
            }
            QPushButton#next_btn:pressed {
                background-color: #2C5282;
            }
            
            /* تصميم الجدول (Table) */
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: transparent;
                selection-background-color: #EBF8FF;
                selection-color: #2B6CB0;
                outline: none;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #EDF2F7;
            }
            
            /* رأس الجدول (Header) */
            QHeaderView::section {
                background-color: #2D3748;
                color: #FFFFFF;
                padding: 15px;
                border: none;
                font-weight: bold;
                font-size: 15px;
            }
            QScrollBar:vertical {
                border: none;
                background: #EDF2F7;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A0AEC0;
            }
        """)
        
        layout = QVBoxLayout()
        
        # قسم إدخال البيانات
        input_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم المريض")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("رقم الهاتف (مثل: 010...)")
        
        input_layout.addWidget(QLabel("الاسم:"))
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(QLabel("الهاتف:"))
        input_layout.addWidget(self.phone_input)
        
        layout.addLayout(input_layout)
        
        # قسم الأزرار
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("إضافة مريض")
        self.add_btn.setObjectName("add_btn")
        self.add_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.add_btn.clicked.connect(self.add_patient)
        
        self.next_btn = QPushButton("إدخال المريض التالي")
        self.next_btn.setObjectName("next_btn")
        self.next_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        self.next_btn.clicked.connect(self.next_patient)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.next_btn)
        
        layout.addLayout(btn_layout)
        
        # جدول عرض طابور الانتظار
        self.table = QTableWidget(0, 4)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["رقم الدور", "الاسم", "الهاتف", "الحالة"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def add_patient(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        
        if not name or not phone:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال الاسم ورقم الهاتف.")
            return
            
        # حساب رقم الدور الجديد لليوم الحالي
        self.cursor.execute("SELECT MAX(queue_number) as max_q FROM patient_queue WHERE DATE(created_at) = CURDATE()")
        result = self.cursor.fetchone()
        next_q = (result['max_q'] or 0) + 1
        
        # الإدراج في قاعدة البيانات
        sql = "INSERT INTO patient_queue (patient_name, phone_number, queue_number, status) VALUES (%s, %s, %s, 'waiting')"
        self.cursor.execute(sql, (name, phone, next_q))
        self.db.commit()
        
        self.name_input.clear()
        self.phone_input.clear()
        self.load_data()
        
        # إرسال البيانات إلى Webhook
        self.send_webhook({
            "event": "new_patient", 
            "name": name, 
            "phone": phone, 
            "queue_number": next_q
        })

    def next_patient(self):
        # 1. تحويل المريض الموجود بالداخل إلى "انتهى"
        self.cursor.execute("UPDATE patient_queue SET status = 'completed' WHERE status = 'in_clinic' AND DATE(created_at) = CURDATE()")
        
        # 2. البحث عن أول مريض في الانتظار
        self.cursor.execute("SELECT id, patient_name, phone_number, queue_number FROM patient_queue WHERE status = 'waiting' AND DATE(created_at) = CURDATE() ORDER BY queue_number ASC LIMIT 1")
        next_p = self.cursor.fetchone()
        
        if next_p:
            # 3. تحويل حالة المريض التالي إلى "بالداخل"
            self.cursor.execute("UPDATE patient_queue SET status = 'in_clinic' WHERE id = %s", (next_p['id'],))
            self.db.commit()
            
            # --- الميزة الجديدة: تنبيه المريض الذي يتبقى أمامه 3 أدوار ---
            # نبحث عن المريض رقم 3 في قائمة الانتظار الحالية (OFFSET 2)
            self.cursor.execute("SELECT id, patient_name, phone_number, queue_number FROM patient_queue WHERE status = 'waiting' AND DATE(created_at) = CURDATE() ORDER BY queue_number ASC LIMIT 1 OFFSET 2")
            approaching_p = self.cursor.fetchone()
            
            if approaching_p:
                # إرسال تنبيه الاقتراب
                self.send_webhook({
                    "event": "approaching_turn", 
                    "name": approaching_p['patient_name'], 
                    "phone": approaching_p['phone_number'], 
                    "queue_number": approaching_p['queue_number']
                })
            # -------------------------------------------------------------
            
            # إرسال إشعار الدخول للمريض الحالي
            self.send_webhook({
                "event": "next_patient", 
                "name": next_p['patient_name'], 
                "phone": next_p['phone_number'], 
                "queue_number": next_p['queue_number']
            })

            # تحديث ملف شاشة العرض
            import json
            current_patient_data = {
                "queue_number": next_p['queue_number'],
                "name": next_p['patient_name']
            }
            with open("current.json", "w", encoding="utf-8") as f:
                json.dump(current_patient_data, f, ensure_ascii=False)
                
            self.load_data()
        else:
            self.db.commit()
            self.load_data()
            QMessageBox.information(self, "تنبيه", "لا يوجد مرضى في قائمة الانتظار حالياً.")

    def load_data(self):
        self.table.setRowCount(0)
        self.cursor.execute("SELECT queue_number, patient_name, phone_number, status FROM patient_queue WHERE DATE(created_at) = CURDATE() ORDER BY queue_number ASC")
        rows = self.cursor.fetchall()
        
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row['queue_number'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row['patient_name']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row['phone_number']))
            
            # عرض الحالة بالعربية
            if row['status'] == 'waiting':
                status_ar = "في الانتظار"
            elif row['status'] == 'in_clinic':
                status_ar = "بالداخل"
            else:
                status_ar = "انتهى"
                
            self.table.setItem(row_idx, 3, QTableWidgetItem(status_ar))
        self.sync_display()

    def send_webhook(self, data):
        try:
            # زيادة المهلة قليلاً لضمان وصول الطلب
            response = requests.post(self.webhook_url, json=data, timeout=3)
            print("---------------------------------")
            print("حالة الاتصال بـ n8n:", response.status_code)
            print("رد السيرفر:", response.text)
            print("---------------------------------")
        except requests.exceptions.RequestException as e:
            print("❌ فشل الاتصال بـ n8n تماماً. السبب:")
            print(e) 
    def sync_display(self):
        import json
        try:
            # 1. جلب المريض الموجود بالداخل حالياً
            self.cursor.execute("SELECT queue_number, patient_name FROM patient_queue WHERE status = 'in_clinic' AND DATE(created_at) = CURDATE() ORDER BY id DESC LIMIT 1")
            current = self.cursor.fetchone()
            
            # 2. جلب قائمة المرضى في الانتظار (الرقم والاسم معاً للتصميم الجديد)
            self.cursor.execute("SELECT queue_number, patient_name FROM patient_queue WHERE status = 'waiting' AND DATE(created_at) = CURDATE() ORDER BY queue_number ASC")
            waiting_records = self.cursor.fetchall()
            
            # تجهيز القائمة بصيغة القاموس التي يطلبها التصميم الجديد
            waiting_list = [{"number": str(r['queue_number']), "name": r['patient_name']} for r in waiting_records]
            
            data = {
                "queue_number": str(current['queue_number']) if current else "",
                "name": current['patient_name'] if current else "",
                "waiting_list": waiting_list
            }
            
            with open("current.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ClinicApp()
    window.show()
    sys.exit(app.exec_())