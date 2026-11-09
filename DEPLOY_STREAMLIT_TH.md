# อัปโหลด Global BAR ขึ้น Streamlit พร้อม Google Sheets

คู่มือนี้ใช้กับโค้ดชุด `github-upload.zip` ที่มีโลโก้ Global BAR และการ์ดจำนวนครั้งเข้าใช้งานด้านล่างหลังล็อกอิน แสดงยอดรวมกับยอดวันนี้ หน้า Login ไม่แสดงตัวนับ

ไฟล์ตัวอย่างไม่มีรหัสผ่านหรือคีย์จริง ต้องใส่ค่าของคุณใน Streamlit Secrets ก่อนใช้งาน ส่วน Service Account JSON จริงต้องสร้างและดาวน์โหลดจาก Google Cloud ตามขั้นตอนด้านล่าง การแก้ไฟล์ตัวอย่างให้เป็นชื่อบัญชีของคุณอย่างเดียวไม่ทำให้เกิดคีย์ที่ใช้ได้

## 1. เตรียมไฟล์อัปโหลด

1. ดาวน์โหลด `github-upload.zip` แล้วคลิกขวา > Extract All / แยกทั้งหมด
2. เปิดโฟลเดอร์ที่แตกไฟล์ จะเห็น `Baccarat_ai.py`, `requirements.txt`, `Globalbar.png`, ไฟล์ Python อื่น และโฟลเดอร์ `.streamlit`
3. ใช้ไฟล์และโฟลเดอร์ที่อยู่ข้างในชุดนี้อัปโหลด อย่าวางทุกไฟล์ไว้ใต้โฟลเดอร์ซ้อนอีกชั้น และอย่าอัปโหลด ZIP เพียงไฟล์เดียว
4. ไฟล์ `.example` เป็นตัวอย่างที่อัปโหลดได้ ตราบใดที่ยังไม่ได้ใส่ข้อมูลลับจริง

ไฟล์ที่มีบทบาทต่างกัน:

| ไฟล์ | ใช้ทำอะไร |
| --- | --- |
| `Baccarat_ai.py` | ไฟล์เริ่มต้นของแอป กรอกชื่อนี้ใน Streamlit |
| `requirements.txt` | ให้ Streamlit ติดตั้งไลบรารี |
| `Bacarat Bg.webp` | ภาพพื้นหลัง วางข้าง `Baccarat_ai.py` และรักษาชื่อไฟล์รวมช่องว่าง |
| `.streamlit/config.toml` | ตั้งค่าธีมและแอป |
| `.streamlit/secrets.google-sheets.toml.example` | แม่แบบค่าที่จะวางในช่อง Secrets สำหรับ Google Sheets |
| `.streamlit/secrets.toml.example` | แม่แบบสำหรับรันในเครื่องและใช้ SQLite |
| `service-account.json.example` | ตัวอย่างหน้าตา JSON ไม่มีคีย์จริง และแอปไม่อ่านไฟล์นี้ |

## 2. อัปโหลดเข้า GitHub

ถ้ามี repository ที่แอปเดิมใช้อยู่แล้ว ให้เปิด repository นั้นและอัปโหลดทับไฟล์ชื่อเดิมใน branch ที่ Streamlit ใช้งาน ไม่จำเป็นต้องสร้างแอปใหม่

สำหรับผู้ที่ยังไม่มี repository:

1. เข้าสู่ระบบ [GitHub](https://github.com/) แล้วสร้าง New repository
2. ตั้งชื่อ เช่น `global-bar-streamlit` เลือก Private หากต้องการจำกัดการเห็นซอร์สโค้ด แล้วกด Create repository
3. ใน repository ใหม่ ใช้ลิงก์ uploading an existing file หากมีรายการไฟล์แล้ว ใช้ Add file > Upload files
4. ลากไฟล์และโฟลเดอร์ทั้งหมดจากภายใน ZIP ที่แตกแล้วไปวาง รวม `.streamlit` และ `tests` เพื่อรักษาโครงสร้างโฟลเดอร์
5. ใส่ข้อความ commit เช่น `Upload Global BAR app` แล้วบันทึกการเปลี่ยนแปลง หาก GitHub ให้สร้าง branch ใหม่ ให้ merge เข้า branch ที่จะใช้ deploy ก่อน
6. ตรวจที่หน้าแรกของ repository ว่ามี `Baccarat_ai.py`, `requirements.txt`, `ui.css`, `Globalbar.png`, `Bacarat Bg.webp` อยู่ระดับบนสุด และมี `.streamlit/config.toml`

หากมองไม่เห็น `.streamlit` ให้เปิด Show > Hidden items ใน File Explorer หากโฟลเดอร์ตกหล่นตอนอัปโหลด ให้ใช้ Add file > Create new file ชื่อ `.streamlit/config.toml` แล้วคัดลอกเนื้อหาจากไฟล์ที่แตกไว้ บันทึกลง branch เดียวกัน

อย่าอัปโหลด JSON ที่ดาวน์โหลดจาก Google Cloud, `.streamlit/secrets.toml` หรือไฟล์ที่กรอกคีย์จริงแล้ว การอัปโหลดผ่านหน้าเว็บ GitHub ต้องเลือกไฟล์เอง แม้โปรเจกต์จะมี `.gitignore` ก็ตาม

อ้างอิง: [GitHub: เพิ่มไฟล์ลง repository](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)

## 3. สร้าง Service Account และดาวน์โหลด JSON จริง

Service Account เป็นบัญชีที่ให้แอปอ่านและเขียนชีต ส่วน Gemini API key ใช้เรียก AI ทั้งสองอย่างใช้แทนกันไม่ได้

1. เปิด [Google Cloud Console](https://console.cloud.google.com/) และเข้าสู่ระบบ Google ของคุณ
2. ที่ตัวเลือกโปรเจกต์ด้านบน เลือกโปรเจกต์เดิมหรือสร้าง New Project เช่น `global-bar` แล้วเลือกให้เป็นโปรเจกต์ปัจจุบัน
3. ไปที่ APIs & Services > Library ค้นหา **Google Sheets API** เปิดรายการแล้วกด Enable ถ้าเปิดอยู่แล้วจะมีปุ่ม Manage
4. ไปที่ IAM & Admin > Service Accounts แล้วกด Create service account
5. ตั้งชื่อ `global-bar-counter` และกด Create and continue
6. ช่องให้สิทธิ์บัญชีนี้กับโปรเจกต์และช่องให้ผู้อื่นเข้าถึงบัญชีนี้เป็นทางเลือก งานนี้ไม่ต้องกำหนด Project Editor ให้เว้นว่างแล้วทำต่อจน Done สิทธิ์เขียนชีตจะให้ผ่าน Share ในขั้นตอนถัดไป
7. คลิกอีเมลของ Service Account ที่เพิ่งสร้าง แล้วเลือกแท็บ Keys
8. กด Add key > Create new key เลือก JSON และกด Create
9. เบราว์เซอร์จะดาวน์โหลดไฟล์ `.json` เก็บไว้ในที่ส่วนตัวนอกโฟลเดอร์ที่จะอัปโหลด GitHub
10. เปิดไฟล์ด้วย Notepad เพื่อดูค่า `client_email` และ `private_key`

Google ให้ดาวน์โหลดคีย์ส่วนตัวครั้งที่สร้างเท่านั้น หากทำไฟล์หายต้องสร้างคีย์ใหม่ หากระบบแจ้งว่าองค์กรไม่อนุญาตให้สร้างคีย์ ให้ติดต่อผู้ดูแลโปรเจกต์หรือองค์กรเพื่อตรวจสิทธิ์และนโยบาย

อ้างอิง: [Google: สร้าง Service Account](https://docs.cloud.google.com/iam/docs/service-accounts-create), [Google: สร้างคีย์ JSON](https://docs.cloud.google.com/iam/docs/keys-create-delete)

## 4. แชร์ Google Sheets ให้บัญชีนี้

เตรียม [Google Sheets สำหรับ Global BAR](https://docs.google.com/spreadsheets/d/1RAzxLD2cZqeOZfQtUHQQHZ3PD5oJo0bLaPx8j55A4Oo/edit) ไว้แล้ว ใช้ไฟล์นี้ต่อได้เลย

1. คัดลอกค่า `client_email` จาก JSON ตัวจริง เช่น `global-bar-counter@ชื่อโปรเจกต์.iam.gserviceaccount.com`
2. เปิดชีต กด Share / แชร์ และเพิ่มอีเมลนั้น
3. เลือกสิทธิ์ **Editor / ผู้แก้ไข** แล้วกด Share หรือ Send ตามปุ่มที่ปรากฏ
4. คง General access เป็น Restricted ได้ ไม่ต้องเปิดให้ทุกคนที่มีลิงก์
5. ตรวจว่าชื่อแท็บด้านล่างคือ `Usage` และ A1 คือ `session_id` ส่วน B1 ใช้ `started_at_utc` แอปจะเติม B1 ให้เมื่อบันทึกครั้งแรกหากยังว่างอยู่

อีเมลที่แชร์ต้องเป็น `client_email` จากไฟล์เดียวกับ private key ที่จะใช้ ไม่ใช่ Gmail ส่วนตัวของคุณ การเชื่อม Google Drive กับแชทไม่ได้ให้สิทธิ์แอป Streamlit โดยอัตโนมัติ

อ้างอิง: [Streamlit: เชื่อมต่อ Google Sheet ส่วนตัว](https://docs.streamlit.io/develop/tutorials/databases/private-gsheet) โค้ดชุดนี้ใช้ Sheets API โดยตรงและต้องการสิทธิ์ Editor เพราะมีการเพิ่มแถว

## 5. เตรียม Secrets จาก JSON

เปิด `.streamlit/secrets.google-sheets.toml.example` เพื่อใช้เป็นแม่แบบ หรือคัดลอกบล็อกนี้ไปที่ช่อง Secrets ของ Streamlit แล้วแทนค่าตัวอย่างทั้งหมด:

```toml
GOOGLE_API_KEY = "REPLACE_WITH_YOUR_GEMINI_API_KEY"
APP_PASSWORD = "REPLACE_WITH_YOUR_MEMBER_PASSWORD"
GEMINI_MODEL = "REPLACE_WITH_YOUR_AVAILABLE_GEMINI_MODEL"

USAGE_STORAGE = "google_sheets"
USAGE_TIMEZONE = "Asia/Shanghai"
USAGE_SHEET_ID = "1RAzxLD2cZqeOZfQtUHQQHZ3PD5oJo0bLaPx8j55A4Oo"
USAGE_SHEET_TAB = "Usage"

[gcp_service_account]
client_email = "REPLACE_WITH_SERVICE_ACCOUNT_EMAIL"
private_key = "-----BEGIN PRIVATE KEY-----\nREPLACE_WITH_PRIVATE_KEY_BODY\n-----END PRIVATE KEY-----\n"
```

| ค่า | เอามาจากไหน |
| --- | --- |
| `GOOGLE_API_KEY` | Gemini API key ของคุณจาก [Google AI Studio](https://aistudio.google.com/apikey) ถ้าคีย์เดิมเคยเปิดเผยให้เปลี่ยนใหม่ |
| `APP_PASSWORD` | รหัสผ่านหน้า Login ที่คุณตั้งเอง |
| `GEMINI_MODEL` | ชื่อโมเดลที่รองรับภาพและ API key ของคุณเรียกได้ หากแอปเดิมทำงานอยู่ให้คงค่าเดิม |
| `USAGE_STORAGE` | คง `google_sheets` เพื่อบันทึกลงชีต |
| `USAGE_TIMEZONE` | `Asia/Shanghai` คือ UTC+8 ตามค่าปัจจุบัน เปลี่ยนเป็น `Asia/Bangkok` หากต้องการให้ “วันนี้” อิงเวลาไทย UTC+7 |
| `USAGE_SHEET_ID` | กรอกไว้ให้ตรงกับชีตที่เตรียมแล้ว เป็นเฉพาะ ID ไม่ใช่ URL เต็ม |
| `USAGE_SHEET_TAB` | ชื่อแท็บ `Usage` ต้องตรงตัวพิมพ์ |
| `client_email` | ค่าจาก JSON ที่ดาวน์โหลดจริง |
| `private_key` | ค่าจาก JSON ไฟล์เดียวกัน ต้องครบตั้งแต่ BEGIN ถึง END |

วิธีคัดลอก private key โดยคง `\n` จาก JSON:

```text
ใน JSON:
"private_key": "-----BEGIN PRIVATE KEY-----\nเนื้อหาคีย์จริง\n-----END PRIVATE KEY-----\n",

ใน Secrets:
private_key = "-----BEGIN PRIVATE KEY-----\nเนื้อหาคีย์จริง\n-----END PRIVATE KEY-----\n"
```

คัดลอกค่าภายในเครื่องหมายคำพูดให้ครบ เปลี่ยนรูปแบบชื่อฟิลด์จาก `"private_key":` เป็น `private_key =` และไม่ใส่ comma ปิดท้าย ไม่ต้องแทน `\n` ด้วยการกด Enter เพราะ TOML อ่าน escape นี้ได้อยู่แล้ว

แอปชุดนี้ใช้เพียง `client_email` และ `private_key` จาก JSON ค่าอื่นไม่ต้องนำมาวาง ไม่ต้องอัปโหลดไฟล์ JSON ให้แอป และไม่ต้องใส่หัวข้อ `[secrets]` ครอบบล็อก

ให้ค่าทั้งหมดตั้งแต่ `GOOGLE_API_KEY` ถึง `USAGE_SHEET_TAB` อยู่ก่อน `[gcp_service_account]` และมีแต่ละคีย์เพียงครั้งเดียว หากแอปมี Secrets เดิมให้เก็บค่าที่ใช้งานได้ แล้วจัดเป็นบล็อกเดียวตามตัวอย่าง ไม่วางบล็อกใหม่ต่อท้ายจนเกิดคีย์หรือหัวข้อซ้ำ

อ้างอิง: [Streamlit: จัดการ Secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)

## 6. Deploy บน Streamlit Community Cloud

สำหรับแอปใหม่:

1. เข้า [Streamlit Community Cloud](https://share.streamlit.io/) และเชื่อมบัญชี GitHub ให้เข้าถึง repository ที่อัปโหลด
2. กด Create app หากถามว่ามีแอปแล้วหรือยัง ให้เลือก Yup, I have an app
3. เลือก Repository เช่น `ชื่อบัญชี/global-bar-streamlit`
4. เลือก Branch ที่มีโค้ดล่าสุด เช่น `main`
5. ใส่ Main file path เป็น `Baccarat_ai.py` ตัวพิมพ์ต้องตรง และไม่ต้องใส่ชื่อ ZIP
6. ตั้ง App URL ตามต้องการถ้าชื่อยังว่าง
7. เปิด Advanced settings เลือก Python **3.12** ซึ่งเป็นรุ่นที่ตรวจโค้ดชุดนี้
8. วาง Secrets ที่เติมค่าจริงจากขั้นตอน 5 ลงช่อง Secrets แล้วกด Save
9. กด Deploy รอระบบติดตั้งไลบรารีจาก `requirements.txt` และเปิด URL ของแอป

สำหรับแอปเดิม:

1. อัปโหลดโค้ดชุดนี้ทับไฟล์เดิมใน repository และ branch ที่เชื่อมกับแอป
2. เปิด Settings > Secrets ของแอป ปรับค่าตามขั้นตอน 5 แล้ว Save
3. หากยังไม่ใช้ค่าใหม่ ให้ Reboot app และเปิดหน้าเว็บใหม่

การอัปเดตโค้ดในครั้งต่อไปทำผ่าน repository และ branch เดิม ส่วนค่าลับแก้ใน Settings > Secrets

อ้างอิง: [Streamlit: Deploy แอป](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)

## 7. ตรวจว่าใช้งานจริงได้

1. เปิด URL หน้า Login ต้องไม่มีการ์ดจำนวนครั้งเข้าใช้งาน
2. ล็อกอินด้วย `APP_PASSWORD` แล้วเลื่อนลงด้านล่าง ต้องพบการ์ด “จำนวนครั้งเข้าใช้งาน” ยอดรวมอยู่ซ้าย และยอดวันนี้อยู่ขวา
3. เปิดแท็บ `Usage` ในชีต ต้องมีรหัส session ใหม่ในคอลัมน์ A และเวลา UTC ในคอลัมน์ B เพิ่ม 1 แถว
4. กดปุ่มหรือวิเคราะห์ภาพซ้ำใน session เดิม ยอดต้องไม่เพิ่มเพราะยังเป็นการเข้าใช้งานรอบเดิม
5. เปิด session ใหม่แล้วล็อกอินสำเร็จ ยอดเพิ่มอีก 1 ครั้ง ยอดเก่าคงอยู่ใน Google Sheets แม้รีบูตแอป
6. อัปโหลดภาพและลองวิเคราะห์หนึ่งครั้งเพื่อตรวจ API key กับโมเดลจริง รวมถึงลองดาวน์โหลดผลสรุป

จำนวนที่แสดงคือรอบการเข้าใช้งานหลังล็อกอิน ไม่ใช่จำนวนบุคคลไม่ซ้ำ ตัวเลข 1,249 ในหน้า preview เป็นข้อมูลสาธิต ไม่ได้ย้ายเข้า Google Sheets และยอด SQLite เดิมไม่ได้ย้ายเข้า Sheets อัตโนมัติ

มีแคชยอด 30 วินาที ยอดจากผู้ใช้อื่นอาจต้องรอแคชหมดและมีการรันหน้าใหม่จึงเห็น การเปิดหน้าไว้เฉย ๆ ไม่ได้รีเฟรชยอดอัตโนมัติ ข้อมูลเก่าที่ไม่มีเวลาอยู่ในยอดรวม แต่ไม่นับเป็นยอดวันนี้

## 8. แก้ปัญหาที่พบบ่อย

ดูรายละเอียดที่ Manage app / Cloud logs โดยอย่าคัดลอกคีย์จริงลงแชท

| อาการ | จุดที่ต้องตรวจ |
| --- | --- |
| ขาด secret / ระบบยังไม่พร้อม | เติมค่าทั้งหมด แทน `REPLACE_WITH_...` และตรวจว่า top-level settings อยู่ก่อน `[gcp_service_account]` |
| บันทึก Secrets ไม่ผ่าน | ใช้ TOML ไม่ใช่ JSON ไม่มี comma ท้ายบรรทัดหรือคีย์ซ้ำ และเครื่องหมายคำพูดต้องครบ |
| Sheets HTTP 403 | เปิด Google Sheets API ในโปรเจกต์ของ Service Account และแชร์ชีตให้ `client_email` เป็น Editor |
| Sheets HTTP 404 | ตรวจ ID ของชีตและสิทธิ์เข้าถึง ไม่ใส่ URL เต็มใน `USAGE_SHEET_ID` |
| ไม่พบแท็บ / หัวตารางไม่ถูกต้อง | แท็บชื่อ `Usage`, A1 เป็น `session_id`, B1 เป็น `started_at_utc` หรือว่างก่อนบันทึกครั้งแรก |
| Invalid JWT / private key / credentials | คัดลอกคีย์ครบจาก JSON จริง ใช้อีเมลจากไฟล์เดียวกัน และตรวจว่าคีย์ยังไม่ถูกลบหรือปิดใช้งาน |
| สร้าง JSON ไม่ได้ | ตรวจสิทธิ์ผู้สร้างคีย์และนโยบายองค์กรกับผู้ดูแล Google Cloud |
| `ModuleNotFoundError` / ไม่พบไฟล์ | อัปโหลดทุกไฟล์จาก ZIP ให้ครบ โดย `requirements.txt` และโมดูลต้องอยู่ข้าง `Baccarat_ai.py` |
| โลโก้หรือสีไม่ขึ้น | ตรวจ `Globalbar.png`, `ui.css` และ `.streamlit/config.toml` รวมตัวพิมพ์เล็กใหญ่ |
| Gemini แจ้ง model not found / 404 | ใช้ชื่อโมเดลจริงที่รองรับภาพและบัญชีคุณเข้าถึงได้ ไม่ใช้ placeholder |
| Gemini แจ้งโควตา / 429 | ตรวจโควตาของ API key และโมเดลที่เลือกในบัญชี Google |

ชุดนี้ตรวจด้วยการทดสอบอัตโนมัติที่จำลอง Gemini และ Google Sheets การเชื่อมจริงจะตรวจได้หลังใส่ Service Account และ API key ของคุณครบแล้ว
