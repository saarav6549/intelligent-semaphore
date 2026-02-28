# מדריך שלב-אחר-שלב: הרצת המערכת על RunPod

## מבוא

המדריך הזה יעזור לך להעלות את מערכת הזיהוי והחישה שלך ל-RunPod ולראות את CARLA רצה על GPU בענן, בזמן שאתה רואה את הכל מהמחשב שלך.

---

## שלב 1: הכנת הקוד

### 1.1 אתחול Git (אם עוד לא עשית)

פתח PowerShell בתיקיית הפרויקט (`c:\dev\intelligent_semaphore`) והרץ:

```powershell
git init
git add .
git commit -m "Initial Team B setup - CARLA + YOLO + VNC"
```

### 1.2 העלאה ל-GitHub (מומלץ)

RunPod יכול למשוך ישירות מ-GitHub:

```powershell
# צור repository חדש ב-GitHub (דרך האתר)
# אחר כך:
git remote add origin https://github.com/[USERNAME]/intelligent-semaphore.git
git branch -M main
git push -u origin main
```

**אלטרנטיבה**: אפשר גם להעלות zip ידנית ל-RunPod (נסביר בהמשך).

---

## שלב 2: הרשמה והתחברות ל-RunPod

### 2.1 כניסה לחשבון

1. לך ל-[runpod.io](https://www.runpod.io)
2. התחבר עם החשבון שלך
3. ודא שיש לך קרדיטים (צריך לראות את היתרה בפינה הימנית למעלה)

### 2.2 הבנת מחירים

**המחירים ב-RunPod (נכון ל-2026)**:
- RTX 4090 (24GB): ~$0.44/hour
- RTX 3090 (24GB): ~$0.34/hour  ✅ **מומלץ להתחלה**
- A6000 (48GB): ~$0.79/hour
- A100 (80GB): ~$2.00/hour

**המלצה שלי**: התחל עם **RTX 3090** - מספיק חזק ל-CARLA + YOLO ולא יקר מדי.

---

## שלב 3: יצירת Pod (השרת בענן)

### 3.1 בחירת Template

1. לחץ על **"Deploy"** בתפריט העליון
2. בחר **"GPU Pods"** (לא Serverless)
3. תראה רשימת GPU זמינים

### 3.2 בחירת GPU

1. חפש **RTX 3090** או **RTX 4090**
2. שים לב ל:
   - **Storage**: לפחות 50GB (CARLA גדולה)
   - **Memory**: 24GB+ RAM מומלץ
   - **Price**: המחיר לשעה
3. לחץ על **"Deploy"** ליד ה-GPU שבחרת

### 3.3 הגדרת Pod

במסך הבא:

**Container Image**:
- בחר: **"RunPod PyTorch"** או **"Custom"**
- אם Custom, שים: `nvidia/cuda:12.1.0-devel-ubuntu22.04`

**Container Disk**:
- לפחות **50GB** (CARLA + models + data)
- מומלץ: **70GB**

**Expose Ports**:
לחץ על **"+ Add Port"** והוסף:
- `2000` (CARLA RPC)
- `8000` (API)
- `6080` (noVNC - זה החשוב!)

**Environment Variables** (אופציונלי):
```
DISPLAY=:99
```

**Volume (אופציונלי)**:
אם אתה רוצה לשמור נתונים בין הפעלות, צור volume של 20-50GB.

### 3.4 לחץ על "Deploy On-Demand"

המערכת תתחיל להקים את ה-Pod. זה לוקח 30-60 שניות.

---

## שלב 4: גישה ל-Pod

### 4.1 פתיחת ה-Pod

אחרי שה-Pod מוכן:
1. תראה אותו ברשימת "My Pods"
2. לחץ על שם ה-Pod
3. תראה מסך עם פרטים

### 4.2 חיבור ל-Terminal של ה-Pod

יש כמה דרכים:

**דרך 1: Web Terminal (הכי קל)**
- לחץ על כפתור **"Connect"** > **"Start Web Terminal"**
- יפתח לך terminal בדפדפן

**דרך 2: SSH**
- העתק את פקודת ה-SSH שמוצגת
- הרץ ב-PowerShell שלך:
```powershell
ssh root@[pod-id].ssh.runpod.io -p [port] -i ~/.ssh/id_rsa
```

---

## שלב 5: התקנת הקוד ב-Pod

### 5.1 חיבור ל-Terminal של ה-Pod

השתמש ב-Web Terminal או SSH.

### 5.2 Clone מ-GitHub (אם העלית)

```bash
cd /workspace
git clone https://github.com/[USERNAME]/intelligent-semaphore.git
cd intelligent-semaphore
```

### 5.3 או: העלאה ידנית

אם לא השתמשת ב-Git:

**ב-Windows (המחשב שלך)**:
```powershell
# דחוס את התיקייה
Compress-Archive -Path c:\dev\intelligent_semaphore\* -DestinationPath intelligent_semaphore.zip
```

**ב-RunPod Terminal**:
```bash
# העלה את הקובץ דרך הממשק או:
cd /workspace
# השתמש ב-RunPod File Manager להעלות את הזיפ
unzip intelligent_semaphore.zip
```

---

## שלב 6: בניית ה-Docker Image

### 6.1 התקנת Docker (אם צריך)

```bash
# בדוק אם Docker מותקן
docker --version

# אם לא, התקן:
apt-get update
apt-get install -y docker.io
```

### 6.2 בניית ה-Image

```bash
cd /workspace/intelligent_semaphore

# בנה את ה-Docker image (זה ייקח 15-30 דקות!)
docker build -t carla-vision-system:latest -f docker/Dockerfile .
```

**הערה**: הבנייה הראשונה לוקחת זמן כי היא מורידה את CARLA (כ-8GB).

---

## שלב 7: הרצת המערכת

### 7.1 הרצת ה-Container

```bash
docker run -d \
  --name carla-system \
  --gpus all \
  -p 2000:2000 \
  -p 8000:8000 \
  -p 6080:6080 \
  -v /workspace/intelligent_semaphore:/workspace \
  carla-vision-system:latest
```

**הסבר הפקודה**:
- `-d`: רץ ברקע (detached)
- `--gpus all`: תן גישה ל-GPU
- `-p 2000:2000`: Port של CARLA
- `-p 8000:8000`: Port של API
- `-p 6080:6080`: Port של noVNC (**החשוב!**)
- `-v`: קישור לקוד שלך (לעדכונים)

### 7.2 בדיקת הלוגים

```bash
# ראה אם הכל עולה בסדר
docker logs -f carla-system
```

תראה משהו כזה:
```
================================================
   Intelligent Traffic Light - Team B System   
================================================
Starting virtual display...
Starting VNC server on port 5900...
Starting noVNC on port 6080...
Starting CARLA server...
Waiting for CARLA to start (30 seconds)...
Starting API server...
================================================
   All services started successfully!          
================================================
```

---

## שלב 8: ראיית CARLA על המסך שלך! 🎉

### 8.1 מציאת ה-URL של noVNC

**ב-RunPod Dashboard**:
1. לך ל-Pod שלך
2. גלול ל-**"TCP Port Mappings"**
3. חפש את Port **6080**
4. תראה משהו כמו: `https://xxxxx-6080.proxy.runpod.net`

### 8.2 פתיחת noVNC

1. העתק את ה-URL של port 6080
2. פתח בדפדפן (Chrome/Firefox/Edge)
3. תראה מסך שחור עם כפתור **"Connect"**
4. לחץ על **"Connect"**
5. **אין צורך בסיסמה** (או אם יבקש: `1234`)

### 8.3 מה תראה

אחרי 30-60 שניות (זמן ההמתנה של CARLA), תתחיל לראות:
- חלון CARLA עם העיר
- סימולציה עם רכבים נוסעים
- כל הגרפיקה מרונדרת על ה-GPU בענן!

---

## שלב 9: בדיקת ה-API

### 9.1 מציאת ה-URL של API

בדיוק כמו noVNC, חפש את port **8000** ב-"TCP Port Mappings":
```
https://xxxxx-8000.proxy.runpod.net
```

### 9.2 פתיחת Swagger UI

פתח בדפדפן:
```
https://xxxxx-8000.proxy.runpod.net/docs
```

תראה ממשק אינטראקטיבי עם כל ה-endpoints!

### 9.3 בדיקות בסיסיות

**בדוק Health**:
```bash
curl https://xxxxx-8000.proxy.runpod.net/health
```

**קבל Observation**:
```bash
curl https://xxxxx-8000.proxy.runpod.net/observation
```

**שלח Action**:
```bash
curl -X POST https://xxxxx-8000.proxy.runpod.net/action \
  -H "Content-Type: application/json" \
  -d '{"action": 2, "duration": 25.0}'
```

### 9.4 ראיית Camera Stream

פתח בדפדפן:
```
https://xxxxx-8000.proxy.runpod.net/camera/stream
```

תראה את המצלמה החיה עם:
- Bounding boxes סביב רכבים (YOLO)
- ROI zones צבעוניים (lanes)
- ספירת רכבים

---

## שלב 10: שיתוף עם חבר צוות A

### מה לתת לחבר צוות A:

**1. ה-API URL שלך:**
```
https://xxxxx-8000.proxy.runpod.net
```

**2. המסמך API_SPEC.md**
(הוא כבר נמצא בתיקייה `docs/`)

**3. דוגמת קוד לשימוש:**

```python
import requests
import numpy as np

API_URL = "https://xxxxx-8000.proxy.runpod.net"

# Get observation
response = requests.get(f"{API_URL}/observation")
obs = response.json()
state = np.array(obs["observation"])  # 8 lanes, normalized [0,1]

print(f"Vehicle counts: {obs['raw_counts']}")
print(f"Normalized state: {state}")

# Send action
action = {"action": 2, "duration": 30.0}
requests.post(f"{API_URL}/action", json=action)
```

---

## טיפים חשובים

### כלכלה וחיסכון

1. **Stop ה-Pod כשלא משתמש בו**:
   - לחץ על **"Stop"** ב-Dashboard
   - זה לא ימחק את הקוד, רק יעצור את החיוב
   - כשתצטרך, לחץ **"Resume"**

2. **Spot Instances** (חיסכון של 50-70%):
   - במקום "On-Demand", בחר "Spot"
   - זול יותר אבל יכול להיסגר אם מישהו שילם יותר
   - מתאים לפיתוח, פחות למשהו קריטי

3. **שעות מומלצות**:
   - אירופה: עבוד בלילה (בארה"ב יום) - יותר זול
   - ארה"ב: עבוד בבוקר

### Performance

1. **CARLA Rendering**:
   - אם לא צריך לראות: שנה ב-`config/carla_config.yaml`:
     ```yaml
     no_rendering_mode: true
     ```
   - זה יחסוך GPU ויאיץ פי 2-3!

2. **YOLO Model Size**:
   - `yolov8n.pt`: הכי מהיר, פחות מדויק
   - `yolov8s.pt`: איזון טוב ✅
   - `yolov8m.pt`: יותר מדויק, יותר איטי
   - התחל עם `n` או `s`

3. **FPS Control**:
   - ב-`config/carla_config.yaml`:
     ```yaml
     fixed_delta_seconds: 0.1  # 10 FPS (מהיר)
     fixed_delta_seconds: 0.05 # 20 FPS (מאוזן)
     fixed_delta_seconds: 0.02 # 50 FPS (איטי, צורך GPU)
     ```

### אבטחה

1. **Password ל-VNC**: כרגע הסיסמה היא `1234`
   - כדי לשנות: ערוך את `docker/entrypoint.sh`
   - הרץ: `x11vnc -storepasswd [NEW_PASSWORD] ~/.vnc/passwd`

2. **API Authentication**: כרגע אין
   - אם צריך, אפשר להוסיף API key
   - שלח לי הודעה ואני אוסיף

---

## פתרון בעיות נפוצות

### בעיה: "Cannot connect to CARLA"

**פתרון 1**: CARLA לוקחת זמן להתחיל
```bash
# בדוק אם CARLA רצה
docker logs carla-system | grep "CARLA"

# אם לא, חכה עוד 30 שניות
```

**פתרון 2**: אתחל את ה-container
```bash
docker restart carla-system
docker logs -f carla-system
```

### בעיה: "Out of GPU memory"

**פתרון**:
```yaml
# קטן את הרזולוציה ב-config/intersection_config.yaml
resolution:
  width: 1280  # במקום 1920
  height: 720  # במקום 1080
```

או שנה ל-GPU יותר חזק (A6000).

### בעיה: noVNC לא נפתח / מסך שחור

**פתרון 1**: חכה 60 שניות - CARLA לוקחת זמן
**פתרון 2**: אתחל VNC
```bash
docker exec -it carla-system bash
pkill x11vnc
x11vnc -display :99 -forever -shared -rfbport 5900 -rfbauth ~/.vnc/passwd &
```

### בעיה: API מחזיר 503 "System not initialized"

**בדיקה**:
```bash
docker logs carla-system | tail -50
```

חפש שגיאות. בדרך כלל זה אומר ש-CARLA עוד לא מוכנה.

### בעיה: YOLO לא מוצא רכבים

**פתרון**: בדוק את ה-ROI zones
```python
# עדכן את config/intersection_config.yaml עם הקואורדינטות הנכונות
# אפשר לראות את הויזואליזציה ב:
# https://xxxxx-8000.proxy.runpod.net/camera/stream
```

---

## פקודות שימושיות

### בדיקת סטטוס

```bash
# האם ה-container רץ?
docker ps

# לוגים של המערכת
docker logs carla-system -f

# שימוש ב-GPU
nvidia-smi
```

### כניסה ל-Container

```bash
# פתח shell בתוך ה-container
docker exec -it carla-system bash

# עכשיו אתה בתוך ה-container!
# אפשר להריץ:
python3 scripts/test_system.py
```

### עצירה והפעלה מחדש

```bash
# עצור
docker stop carla-system

# הפעל מחדש
docker start carla-system

# מחק לגמרי (אם צריך לבנות מחדש)
docker rm -f carla-system
```

### עדכון קוד

אם שינית משהו בקוד:

**אופציה 1: בלי rebuild** (מהיר)
```bash
# הקוד ממופה עם volume, אז שינויים מתעדכנים אוטומטית
# רק תאתחל את ה-API:
docker exec carla-system pkill -f uvicorn
docker exec carla-system bash -c "cd /workspace && python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8000 &"
```

**אופציה 2: Rebuild מלא** (אם שינית Dockerfile)
```bash
docker stop carla-system
docker rm carla-system
docker build -t carla-vision-system:latest -f docker/Dockerfile .
# אחר כך הרץ שוב את docker run...
```

---

## קובץ .env לחבר צוות A

צור קובץ שחבר צוות A יוכל להשתמש בו:

**`team_b_config.env`**:
```bash
# Team B Vision System Configuration
TEAM_B_API_URL=https://xxxxx-8000.proxy.runpod.net
TEAM_B_CAMERA_STREAM=https://xxxxx-8000.proxy.runpod.net/camera/stream
TEAM_B_NOVNC_URL=https://xxxxx-6080.proxy.runpod.net
NUM_LANES=8
NUM_PHASES=5
```

---

## זרימת עבודה מומלצת

### שלב 1: פיתוח ראשוני (1-2 שעות GPU)
1. הפעל Pod
2. בדוק שהכל עובד
3. כוונן ROI zones
4. צור dataset ל-YOLO (אם צריך)
5. עצור Pod

### שלב 2: אימון YOLO (2-4 שעות GPU)
1. הפעל Pod
2. הרץ `python yolo_detection/train_yolo.py`
3. המתן לסיום
4. שמור weights
5. עצור Pod

### שלב 3: אינטגרציה עם Team A (משתנה)
1. הפעל Pod
2. תן לחבר צוות A את ה-URL
3. הוא מריץ את האימון של PPO
4. אתה עוקב ב-noVNC
5. עצור כשסיימתם

---

## FAQ

**ש: כמה זה עולה?**
ת: RTX 3090 = $0.34/שעה. 10 שעות עבודה = $3.40

**ש: מה קורה אם ה-Pod נסגר פתאום?**
ת: אם Volume מחובר, הנתונים נשמרים. אחרת - הכל נמחק.

**ש: אפשר להשהות ולחזור מאוחר יותר?**
ת: כן! Stop ה-Pod (לא Terminate). שלם רק על storage ($0.10/GB/חודש).

**ש: איך אני שומר את ה-YOLO weights שאימנתי?**
ת: הם נשמרים ב-`/workspace/runs/train/`. תוריד אותם:
```bash
# מה-Pod Terminal:
zip -r yolo_weights.zip runs/train/

# אחר כך השתמש ב-RunPod File Manager להוריד
```

**ש: למה CARLA לא נפתח ב-noVNC?**
ת: חכה 30-60 שניות. CARLA לוקחת זמן להתחיל. בדוק logs.

**ש: איך אני מכבה את המערכת?**
ת: 
```bash
docker stop carla-system  # עוצר את ה-container
# ב-RunPod Dashboard: Stop או Terminate את ה-Pod
```

---

## צעדים הבאים

1. ✅ העלה את הקוד ל-RunPod
2. ✅ ודא ש-CARLA רצה ונראית ב-noVNC
3. ✅ בדוק את ה-API endpoints
4. 🔄 כוונן את ה-ROI zones (ייקח ניסוי וטעייה)
5. 🔄 צור dataset ואמן YOLO
6. 🔄 שתף את ה-API URL עם חבר צוות A
7. 🔄 התחילו אימון!

---

## עזרה נוספת

אם משהו לא עובד:
1. בדוק את הלוגים: `docker logs carla-system`
2. היכנס ל-container: `docker exec -it carla-system bash`
3. הרץ בדיקות: `python3 scripts/test_system.py`
4. שלח לי את השגיאה ואני אעזור!

**בהצלחה! 🚦🚗**
