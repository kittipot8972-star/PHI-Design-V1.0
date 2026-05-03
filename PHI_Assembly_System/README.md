# PHI Integration Design — Assembly System

ระบบเลือก Solenoid Valve + ประกอบ STEP Assembly อัตโนมัติ

---

## โครงสร้างโฟลเดอร์

```
PHI-Design-V1.0/
├── Solenoid_Valve_Selector.html   ← หน้าเว็บหลัก (เปิดใน browser)
├── start.sh                       ← สคริปต์เริ่ม API (Mac/Linux)
│
├── assembler/
│   ├── api.py                     ← Flask API backend
│   ├── assemble.py                ← CadQuery assembly engine
│   └── requirements.txt           ← Python dependencies
│
├── assembly_rules/
│   └── positions.json             ← ระยะห่างแต่ละชิ้น (จาก SMC datasheet)
│
├── models/                        ← STEP files จาก SMC (วางเองหลังดาวน์โหลด)
│   ├── solenoid/
│   │   ├── SY5320-5LZ-01.step
│   │   ├── SY5420-5LZ-01.step
│   │   └── ...
│   ├── manifold/
│   │   ├── SS5Y5-20-04.step
│   │   └── ...
│   └── blanking/
│       └── SY5000-26-20A.step
│
├── previews/                      ← PNG preview (optional)
│   └── SY5320-5LZ-01.png
│
└── output/                        ← STEP output (auto-generated)
```

---

## วิธีใช้งาน

### 1. ติดตั้ง Python (ครั้งแรกครั้งเดียว)

```bash
# Mac
brew install python3

# Windows — ดาวน์โหลดจาก python.org
```

### 2. ติดตั้ง dependencies

```bash
pip install cadquery flask flask-cors
```

### 3. เริ่ม API

```bash
# Mac / Linux
bash start.sh

# Windows
python assembler/api.py
```

API จะรันที่ `http://localhost:5050`

### 4. เปิดเว็บ

เปิดไฟล์ `Solenoid_Valve_Selector.html` ใน browser
กด **⚙ ตั้งค่า** ตรวจสอบ API URL → `http://localhost:5050`

---

## วิธีเพิ่ม STEP Files จริง (จาก SMC)

1. ไปที่ **https://www.smcworld.com** → Products → ค้นหา Part No.
2. เลือก **CAD Data** → Format: **STEP (AP214)**
3. ดาวน์โหลดและเปลี่ยนชื่อไฟล์ให้ตรง Part No. เช่น `SY5420-5LZ-01.step`
4. วางใน `models/solenoid/` หรือ `models/manifold/`
5. ระบบจะโหลดไฟล์จริงอัตโนมัติ (ไม่ต้องแก้โค้ด)

---

## API Endpoints

| Method | URL | คำอธิบาย |
|--------|-----|----------|
| GET | `/health` | ตรวจสถานะ API |
| POST | `/api/assemble` | สร้าง STEP (รอจนเสร็จ) |
| POST | `/api/assemble-async` | สร้าง STEP (background) |
| GET | `/api/job/<id>` | ดู status |
| GET | `/api/download/<id>` | ดาวน์โหลด STEP |

### ตัวอย่าง POST body

```json
{
  "bom": [
    {"series": "SY5", "orientation": "H", "part_no": "SY5420-5LZ-01", "qty": 3},
    {"series": "SY5", "orientation": "V", "part_no": "SY5320-5LZ-01", "qty": 1}
  ],
  "name": "My_Assembly"
}
```

---

## Deploy บน Server (Railway / Render)

```bash
# Railway
railway login
railway init
railway up

# กำหนด environment variable
PORT=5050
```

เปลี่ยน API URL ในเว็บจาก `localhost:5050` เป็น URL ของ server
