# Global BAR · AI Vision Scanner

แอป Streamlit สำหรับอัปโหลดภาพและแสดงผลวิเคราะห์จาก Gemini Vision ใช้ Prompt เดิม รวมถึงการจำลองผล 20 ไม้ แสดงคำตอบแบบ streaming พร้อมดาวน์โหลดผลสรุป

**สำหรับอัปโหลดขึ้นเว็บ:** อ่าน [คู่มือ Streamlit และ Service Account JSON แบบทีละขั้น](DEPLOY_STREAMLIT_TH.md) ใช้ `.streamlit/secrets.google-sheets.toml.example` สำหรับเก็บยอดใน Google Sheets ส่วน `service-account.json.example` เป็นตัวอย่างรูปแบบเท่านั้น ไม่มีคีย์จริง

## ตั้งค่าก่อนใช้งาน

แอปต้องใช้ค่าทั้งสามนี้จาก Streamlit Secrets ไม่มี API key รหัสผ่าน หรือโมเดลสำรองฝังอยู่ในโค้ด:

```toml
GOOGLE_API_KEY = "ใส่_API_KEY_ใหม่ของคุณ"
APP_PASSWORD = "ตั้งรหัสสมาชิกของคุณ"
GEMINI_MODEL = "REPLACE_WITH_YOUR_AVAILABLE_GEMINI_MODEL"
```

แทนค่า `GEMINI_MODEL` ด้วยชื่อรุ่นที่รองรับภาพและบัญชี Google ของคุณเข้าถึงได้ ถ้าแอปเดิมใช้งานสำเร็จ ให้ใช้ค่าเดิม ทดสอบกับ API และภาพจริงก่อนเปิดให้สมาชิกใช้งาน การเปลี่ยนโมเดลไม่เปลี่ยน Prompt แต่คำตอบและเวลาอาจต่างกัน

หาก API key เดิมเคยถูกเปิดเผย ให้เพิกถอนหรือเปลี่ยนคีย์ที่ Google AI Studio แล้วใช้คีย์ใหม่ ห้ามใส่ API key จริงหรือรหัสผ่านจริงลงใน repository

## รันบนเครื่อง

1. ใช้ Python 3.12 และเปิด Terminal ในโฟลเดอร์โปรเจกต์
2. ติดตั้ง dependency:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. คัดลอก `.streamlit/secrets.toml.example` เป็น `.streamlit/secrets.toml` แล้วแก้ค่าตัวอย่างให้เป็นค่าจริง
4. เริ่มแอป:

   ```powershell
   python -m streamlit run Baccarat_ai.py --global.developmentMode false
   ```

5. เปิด URL จาก Terminal และใช้รหัสที่ตั้งใน `APP_PASSWORD`

## อัปโหลด GitHub

แตกไฟล์ `dist/github-upload.zip` แล้วอัปโหลดไฟล์ข้างใน โดยรักษาโครงสร้างนี้และตัวพิมพ์เล็ก–ใหญ่ ไม่ใช่อัปโหลด ZIP อย่างเดียว:

```text
Baccarat_ai.py
app_settings.py
scanner.py
usage_counter.py
sheets_counter.py
ui.css
Globalbar.png
Bacarat Bg.webp
requirements.txt
README.md
DEPLOY_STREAMLIT_TH.md
service-account.json.example
.gitignore
.streamlit/
    config.toml
    secrets.toml.example
    secrets.google-sheets.toml.example
tests/
    test_scanner.py
    test_app_settings.py
    test_usage_counter.py
    test_usage_ui.py
    test_sheets_counter.py
```

ไฟล์ `Globalbar.png` เป็นโลโก้ที่ใช้ทั้งหน้าเข้าสู่ระบบ หน้าวิเคราะห์ และไอคอนแท็บ ต้องอัปโหลดไว้ระดับเดียวกับ `Baccarat_ai.py` โดยใช้ชื่อไฟล์ตรงตามนี้ ธีมใช้สีน้ำเงิน กรมท่า และสีเงินให้เข้ากับโลโก้ ไม่ต้องอัปโหลดโฟลเดอร์ dependency, skills, __pycache__, ภาพทดสอบ หรือ dist ไฟล์ `.streamlit/secrets.toml` ถูก ignore แต่ถ้าใช้ Upload files ผ่านหน้า GitHub ต้องตรวจเองว่าไม่ได้เลือกไฟล์นี้

ไฟล์ `Bacarat Bg.webp` เป็นภาพพื้นหลังทั้งหน้าเข้าสู่ระบบและหน้าวิเคราะห์ ให้อัปโหลดไว้ข้าง `Baccarat_ai.py` เช่นเดียวกัน โดยรักษาชื่อไฟล์และช่องว่างให้ตรงตามนี้ เว็บใช้ชั้นสีกรมท่าโปร่งแสงใน `ui.css` เพื่อให้ภาพเข้ากับธีมและข้อความอ่านง่าย พร้อมปรับตำแหน่งภาพบนมือถือ หากไม่มีไฟล์ภาพ แอปยังเปิดได้ด้วยพื้นหลังกรมท่าเดิม

## Deploy บน Streamlit Community Cloud

1. สร้าง repository บน GitHub และอัปโหลดไฟล์ตามรายการข้างต้น
2. เข้า https://share.streamlit.io แล้วเชื่อม GitHub ให้เข้าถึง repository นี้
3. เลือก Create app และเลือก repository กับ branch ที่มีไฟล์จริง
4. ตั้ง Main file path เป็น `Baccarat_ai.py`
5. ใน Advanced settings เลือก Python 3.12
6. วางค่าจริงทั้งสามรายการจากหัวข้อ “ตั้งค่าก่อนใช้งาน” ลงช่อง Secrets โดยไม่ต้องมีหัวข้อ `[secrets]`
7. Save แล้ว Deploy รอการติดตั้ง dependency และเปิด URL ที่ได้รับ
8. ทดสอบรหัสผิด รหัสถูก อัปโหลดภาพ วิเคราะห์ครบ 20 ไม้ และดาวน์โหลดผลสรุป

แก้ API key รหัสผ่าน หรือชื่อโมเดลภายหลังที่ Settings > Secrets แล้วบันทึก/รีบูตแอปตามจำเป็น อัปเดตโค้ดผ่าน commit ใน branch ที่ผูกกับแอป

## ตรวจปัญหา

- หน้าแจ้งระบบยังไม่พร้อม: ตรวจ Cloud logs ว่าขาด secret ตัวใด ชื่อคีย์ต้องตรงและค่าไม่เป็นช่องว่างหรือตัวอย่าง
- `ModuleNotFoundError`: ตรวจว่าอัปโหลด `app_settings.py`, `scanner.py`, `usage_counter.py`, `sheets_counter.py` และ `requirements.txt` ครบ
- ไม่พบ CSS: ต้องมี `ui.css` ข้าง `Baccarat_ai.py`
- วิเคราะห์ไม่สำเร็จ: ตรวจ API key สิทธิ์เข้าถึงโมเดล โควตา และการเชื่อมต่อ โดยหน้าแอปจะไม่แสดงคีย์หรือรายละเอียดข้อผิดพลาดภายใน

## เก็บยอดถาวรใน Google Sheets

เตรียม [Google Sheets สำหรับ Global BAR](https://docs.google.com/spreadsheets/d/1RAzxLD2cZqeOZfQtUHQQHZ3PD5oJo0bLaPx8j55A4Oo/edit) ไว้แล้ว ในแท็บ `Usage` มีหัวคอลัมน์ A1 เป็น `session_id` และยังไม่มีข้อมูลผู้ใช้งาน ชีตอยู่ในโฟลเดอร์ ChatGPT ของ Google Drive

### 1. เตรียมบัญชีสำหรับแอป

1. เปิด [Google Cloud Console](https://console.cloud.google.com/) แล้วเลือกหรือสร้างโปรเจกต์
2. ไปที่ APIs & Services > Library ค้นหา **Google Sheets API** และกด Enable
3. ไปที่ IAM & Admin > Service Accounts > Create service account ตั้งชื่อ เช่น `global-bar-counter` โดยไม่ต้องให้สิทธิ์ Project Editor สำหรับงานนี้
4. เปิด Service Account ที่สร้าง ไปที่ Keys > Add key > Create new key > JSON แล้วดาวน์โหลดไฟล์ เก็บไฟล์นี้เป็นความลับ ไม่อัปโหลดเข้า GitHub หรือส่งในแชท
5. เปิดชีตที่เตรียมไว้ กด Share เพิ่มอีเมลจากค่า `client_email` ใน JSON และให้สิทธิ์ **Editor** แก่บัญชีนั้น ไม่ต้องเปิดชีตเป็นสาธารณะ

การสร้างชีตผ่านบัญชี Google ที่เชื่อมกับแชทไม่ได้ให้สิทธิ์แอป Streamlit เขียนชีตโดยอัตโนมัติ แอปต้องใช้ Service Account ของตัวเองตามขั้นตอนนี้ อ้างอิง [Streamlit: private Google Sheet](https://docs.streamlit.io/develop/tutorials/databases/private-gsheet) และ [Google: service accounts](https://developers.google.com/identity/protocols/oauth2/service-account)

### 2. ตั้งค่า Streamlit Secrets

อัปโหลดโค้ดชุดใหม่รวม `sheets_counter.py` และ `requirements.txt` จากนั้นเปิด Settings > Secrets ของแอป คงค่า `GOOGLE_API_KEY`, `APP_PASSWORD`, `GEMINI_MODEL` เดิม แล้วเพิ่มค่าด้านล่าง **ก่อนหัวข้อ `[gcp_service_account]`**:

```toml
USAGE_STORAGE = "google_sheets"
USAGE_TIMEZONE = "Asia/Shanghai"
USAGE_SHEET_ID = "1RAzxLD2cZqeOZfQtUHQQHZ3PD5oJo0bLaPx8j55A4Oo"
USAGE_SHEET_TAB = "Usage"

[gcp_service_account]
client_email = "คัดลอกค่า client_email จากไฟล์ JSON"
private_key = """-----BEGIN PRIVATE KEY-----
วางเนื้อหา private_key จริงจากไฟล์ JSON ตรงนี้
-----END PRIVATE KEY-----
"""
```

คัดลอกค่า private_key ครบทั้งส่วน BEGIN, เนื้อหาคีย์ และ END รองรับทั้งขึ้นบรรทัดใหม่จริงหรือ `\n` จาก JSON อย่าวางคีย์ในไฟล์ Python หากมี `[gcp_service_account]` อยู่แล้วให้แก้หัวข้อเดิม ไม่สร้างซ้ำ ค่าระดับบนสุดต้องอยู่ก่อนหัวข้อ TOML ทุกหัวข้อ

กด Save และ Reboot app สำหรับเครื่องตัวเองให้ใส่ค่าเดียวกันใน `.streamlit/secrets.toml`

### 3. ตรวจหลังเชื่อมต่อ

1. เปิดหน้าล็อกอิน: ไม่แสดงตัวนับและไม่อ่านหรือเขียนยอดในชีต
2. เข้าสู่ระบบสำเร็จ: ในคอลัมน์ A ของ `Usage` ต้องมีรหัสสุ่มใหม่ 1 แถว คอลัมน์ B เก็บเวลาเริ่มเข้าใช้งานแบบ UTC และหน้าเว็บเพิ่มยอดรวมกับยอดวันนี้ 1 ครั้ง
3. กดใช้งานหรือวิเคราะห์ซ้ำในรอบเดิม: ไม่เพิ่มแถวหรือยอด
4. รีสตาร์ตแอปแล้วเข้าสู่ระบบใน session ใหม่: ยอดเดิมจากชีตยังอยู่และเพิ่มอีก 1 ครั้ง โดยแสดงตัวนับด้านล่างหน้าวิเคราะห์ ก่อนส่วนท้ายเว็บ

แอปนับรหัส session ไม่ซ้ำจากชีต โดยใช้ Sheets API แบบ append จึงไม่เขียนทับยอดรวมขณะหลายคนเข้าใช้งานพร้อมกัน มีแคช 30 วินาทีเพื่อลดการเรียก API; ยอดจากแอปอีก instance จะเห็นหลังแคชหมดและมีการรันหน้าใหม่ ไม่มีการรีเฟรชยอดอัตโนมัติขณะเปิดหน้าทิ้งไว้

การ์ดแสดง “เข้าใช้งานทั้งหมด” ด้านซ้ายและ “วันนี้” ด้านขวา โดยวันนี้คำนวณตาม `USAGE_TIMEZONE` ค่าเริ่มต้นคือ `Asia/Shanghai` (UTC+8) หากต้องการนับตามเวลาไทยให้เปลี่ยนเป็น `Asia/Bangkok` (UTC+7) ค่าต้องอยู่ก่อนหัวข้อ TOML ทุกหัวข้อ เวลาในฐานข้อมูลเก็บเป็น UTC จึงเปลี่ยนเขตเวลาสำหรับการแสดงผลได้

ชีตรุ่นเก่าที่มีคอลัมน์ A อย่างเดียวใช้งานต่อได้ แอปจะเพิ่มหัวข้อ `started_at_utc` ใน B1 เมื่อบันทึกรอบใหม่ โดยจะไม่เขียนทับหาก B1 เป็นหัวข้ออื่น ข้อมูลเก่าที่ไม่มีเวลายังคงนับในยอดรวม แต่ไม่เดาว่าเป็นการเข้าใช้งานของวันนี้

เมื่อ Google ขัดข้อง ตัวนับจะแจ้งไม่พร้อมแสดงและไม่สลับไปใช้ยอด SQLite แอปยังใช้งานได้ และลองส่ง session เดิมอีกครั้งเมื่อรันใหม่ หากปิด session ก่อนส่งสำเร็จ รอบนั้นอาจไม่ถูกบันทึก การส่งซ้ำหรือแถวซ้ำของรหัสเดียวกันจะถูกนับเพียงครั้งเดียว

ยอดเดิมใน SQLite ยังอยู่ในไฟล์เดิม และไม่ได้ย้ายเข้า Sheets อัตโนมัติ ชีตใหม่เริ่มนับจากศูนย์ อย่าลบหรือแก้คอลัมน์ A:B ของชีตที่ใช้งานแล้ว เพราะเป็นข้อมูลต้นทางของยอดรวมและยอดวันนี้

### ถ้าตัวนับแจ้งว่าไม่พร้อมแสดง

- Cloud logs แสดง HTTP 403: ตรวจว่าเปิด Sheets API และแชร์ชีตให้ `client_email` เป็น Editor แล้ว
- HTTP 404: ตรวจ `USAGE_SHEET_ID` และสิทธิ์เข้าถึงชีต
- HTTP 400 หรือข้อความเกี่ยวกับหัวตาราง: ตรวจชื่อแท็บ `Usage` หัวข้อ A1 ต้องเป็น `session_id` และ B1 ต้องเป็น `started_at_utc` หรือว่างสำหรับชีตรุ่นเก่า
- HTTP 429: Google จำกัดจำนวนคำขอ รอสักครู่แล้วลองใหม่ ดู [โควตา Sheets API](https://developers.google.com/workspace/sheets/api/limits)
- Invalid service account configuration: ตรวจว่า private_key ถูกคัดลอกครบและตรงกับ client_email
- ไม่ใช้ `GOOGLE_API_KEY` ของ Gemini แทนคีย์ Service Account ทั้งสองส่วนใช้การยืนยันตัวตนต่างกัน

## พฤติกรรมและข้อจำกัด

### จำนวนการเข้าใช้งาน

- แสดงยอดสะสมเฉพาะหลังเข้าสู่ระบบ โดยอยู่ด้านล่างหน้าวิเคราะห์ ก่อนส่วนท้ายเว็บ หน้า Login ไม่แสดงหรือดึงยอด เริ่มนับจากวันที่ติดตั้งตัวนับนี้ ไม่มีข้อมูลย้อนหลังจากเวอร์ชันก่อน
- นับเฉพาะการเข้าสู่ระบบสำเร็จ 1 ครั้งต่อ Streamlit session การเปิดหน้าล็อกอิน กรอกรหัสผิด กดปุ่ม หรือวิเคราะห์ภาพซ้ำใน session เดิมจะไม่เพิ่มยอด
- เมื่อ session ใหม่เข้าสู่ระบบสำเร็จจะเพิ่ม 1 ครั้ง รวมถึงการรีเฟรชหน้าเว็บหรือเปิดแท็บใหม่ที่สร้าง session ใหม่ จึงเป็นจำนวนรอบการเข้าใช้งาน ไม่ใช่จำนวนบุคคลไม่ซ้ำหรือจำนวนคนออนไลน์
- หากไม่ได้ตั้ง `USAGE_STORAGE` จะใช้ SQLite ที่ `data/usage.sqlite3` ตั้ง `google_sheets` เพื่อใช้ชีตตามขั้นตอนข้างบน ทั้งสองแบบเก็บรหัส session แบบสุ่มและเวลาเข้าใช้งาน ไม่มีชื่อ IP รหัสผ่าน หรือภาพ
- ยอดวันนี้นับรอบที่เริ่มเข้าสู่ระบบในวันนั้น ไม่เพิ่มยอดรายวันใหม่ให้ session เดิมเมื่อเปิดค้างข้ามวัน จะเห็นยอดของวันใหม่เมื่อหน้ารันอีกครั้ง SQLite รุ่นเก่าจะเพิ่มคอลัมน์เวลาอัตโนมัติโดยรักษายอดรวมเดิม
- SQLite ใช้ยอดร่วมกันระหว่างผู้ใช้ที่ใช้ไฟล์ฐานข้อมูลเดียวกัน และคงอยู่หลังรีสตาร์ตกระบวนการตราบที่ไฟล์ยังอยู่ ไม่ต้องอัปโหลดฐานข้อมูลไป GitHub
- **Streamlit Community Cloud ไม่รับประกันการเก็บไฟล์ภายในเครื่อง** ยอด SQLite อาจหายเมื่อระบบล้างหรือสร้างเครื่องใหม่ ส่วนยอดใน Google Sheets อยู่ภายนอกแอป ดู [เอกสาร Streamlit](https://docs.streamlit.io/develop/concepts/connections/connecting-to-data)
- หากฐานข้อมูลไม่พร้อม จะแสดงว่าไม่พร้อมแสดงยอดชั่วคราว แอปยังวิเคราะห์ภาพได้ และจะลองบันทึก session เดิมอีกครั้งเมื่อแอปรันใหม่

### การวิเคราะห์ภาพ

- รับ JPG/PNG ไม่เกิน 10 MB ธีมอยู่ใน `ui.css` และ `.streamlit/config.toml`
- ส่งไฟล์ JPEG เดิมหรือ PNG ที่เล็กกว่าโดยไม่ลดความละเอียด
- Streaming ช่วยให้เริ่มอ่านก่อนรายงานจบ ไม่รับประกันว่าเวลาสร้างคำตอบทั้งหมดจะลดลง
- ใช้ผลภาพเดิมซ้ำภายใน session เดิม กด “วิเคราะห์ภาพนี้ใหม่” เพื่อเรียก AI อีกครั้ง
- แสดงเวลาข้อความแรกและเวลารวม การรีเฟรชเบราว์เซอร์หรือรีสตาร์ตเซิร์ฟเวอร์อาจทำให้ session หาย
- ระบบใช้รหัสผ่านร่วม ยังไม่มีบัญชีแยกสมาชิก การแก้รหัสไม่บังคับออกจาก session ที่เข้าสู่ระบบแล้ว
- ภาพถูกส่งไปยัง Google เพื่อวิเคราะห์ และผลทำนายเป็นคำตอบของ AI ไม่มีผลทดสอบความแม่นยำรองรับในแอป
- โค้ดยังใช้ SDK `google-generativeai` ตามเดิม การย้ายไป SDK ใหม่ต้องแก้ส่วนเรียก API ประกอบกัน

## ทดสอบ

```powershell
python -m unittest discover -s tests -v
```

การทดสอบอัตโนมัติใช้ Google Sheets จำลองและไม่เรียก Gemini จริง ต้องทดสอบสิทธิ์ Service Account, การอ่าน/เขียนชีต และโมเดลจริงบน deployment เพิ่มเติม
