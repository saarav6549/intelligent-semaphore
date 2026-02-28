# 🚀 START HERE - Team B Member

## ברוך הבא למערכת הזיהוי והחישה!

אתה **Team B** - אחראי על CARLA, YOLO, והחיבור לענן.

---

## צעדים ראשונים (5 דקות)

### 1. ודא שהכל מותקן

```powershell
# בדוק Python
python --version

# בדוק Git
git --version

# התקן dependencies
cd c:\dev\intelligent_semaphore
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

📖 **עזרה מפורטת**: `docs/WINDOWS_SETUP.md`

---

### 2. קרא את הקונפיגורציה

פתח וקרא (לא לערוך עדיין):
- `config/intersection_config.yaml` - מבנה הצומת
- `config/carla_config.yaml` - הגדרות CARLA
- `config/yolo_config.yaml` - הגדרות YOLO

---

### 3. העלה ל-GitHub

```powershell
git init
git add .
git commit -m "Initial Team B setup"

# צור repo ב-github.com ואז:
git remote add origin https://github.com/[USERNAME]/intelligent-semaphore.git
git push -u origin main
```

---

## העלאה ל-RunPod (30-60 דקות)

### שלב 1: כניסה ל-RunPod

1. לך ל-[runpod.io](https://www.runpod.io)
2. התחבר לחשבון
3. ודא שיש קרדיטים

### שלב 2: יצירת Pod

1. לחץ **"Deploy"** > **"GPU Pods"**
2. בחר **RTX 3090** (מאוזן) או **RTX 4090** (חזק יותר)
3. Storage: **50-70 GB**
4. Expose ports: **2000, 8000, 6080**
5. לחץ **"Deploy On-Demand"**

### שלב 3: התקנת הקוד

ב-RunPod Web Terminal:

```bash
cd /workspace
git clone https://github.com/[USERNAME]/intelligent-semaphore.git
cd intelligent-semaphore

# Build Docker image (15-30 minutes!)
docker build -t carla-vision-system:latest -f docker/Dockerfile .

# Run container
docker run -d \
  --name carla-system \
  --gpus all \
  -p 2000:2000 \
  -p 8000:8000 \
  -p 6080:6080 \
  -v /workspace/intelligent_semaphore:/workspace \
  carla-vision-system:latest

# Wait 60 seconds for CARLA to start, then check:
docker logs -f carla-system
```

### שלב 4: בדיקה

1. **noVNC** (ראיית CARLA): `https://[pod-id]-6080.proxy.runpod.net`
2. **API Docs**: `https://[pod-id]-8000.proxy.runpod.net/docs`
3. **Camera Stream**: `https://[pod-id]-8000.proxy.runpod.net/camera/stream`

📖 **מדריך מפורט**: `docs/RUNPOD_SETUP.md`

---

## שיתוף עם Team A

תן לחבר צוות A:

1. ✅ **API URL**: `https://[pod-id]-8000.proxy.runpod.net`
2. ✅ **הקובץ**: `TEAM_A_INTEGRATION.md`
3. ✅ **הקובץ**: `docs/API_SPEC.md`

הוא יכול להתחיל לאמן את ה-PPO שלו!

---

## תפעול יומיומי

### בוקר (התחלת עבודה)

```bash
# ב-RunPod Dashboard
1. לחץ "Start" על ה-Pod
2. חכה דקה
3. docker start carla-system
4. docker logs -f carla-system  # ודא שהכל עולה
```

### ערב (סיום עבודה)

```bash
# ב-RunPod Dashboard
1. docker stop carla-system
2. לחץ "Stop" על ה-Pod
3. זהו! לא תחויב עד שתפעיל מחדש
```

---

## המשימות שלך

### ✅ עכשיו (Setup)
- [x] התקן Python, Git
- [x] Clone הקוד
- [x] העלה ל-RunPod
- [x] ודא שהכל עובד

### 🔄 השבוע (Development)
- [ ] כוונן ROI zones (הקואורדינטות של הנתיבים)
- [ ] צור dataset מ-CARLA: `python scripts/generate_dataset.py`
- [ ] אמן YOLO: `python yolo_detection/train_yolo.py`
- [ ] בדוק דיוק זיהוי ב-camera stream

### 🔄 שבוע הבא (Integration)
- [ ] שתף API URL עם Team A
- [ ] תאם על reward function
- [ ] עקוב אחרי האימון ב-noVNC
- [ ] תקן bugs שמופיעים

### 🔄 לקראת הסוף (Optimization)
- [ ] אופטימיזציה של ROI mapping
- [ ] Fine-tuning של YOLO
- [ ] הרצת benchmark tests
- [ ] הכנת presentation

---

## עזרה מהירה

| בעיה | פתרון |
|------|--------|
| לא מצליח להתחבר ל-CARLA | `docker logs carla-system` |
| YOLO לא מזהה | בדוק `config/yolo_config.yaml` |
| ROI לא עובד | כוונן ב-`config/intersection_config.yaml` |
| API לא עובד | `docker restart carla-system` |

📖 **פתרון בעיות מלא**: `docs/TROUBLESHOOTING.md`

---

## קבצים חשובים לקרוא

1. `README.md` - סקירה כללית
2. `docs/RUNPOD_SETUP.md` - מדריך RunPod מלא (עברית!)
3. `docs/API_SPEC.md` - מפרט API ל-Team A
4. `TEAM_A_INTEGRATION.md` - מה לתת ל-Team A

---

## פקודות מהירות

```bash
# Test everything
python scripts/test_system.py

# Quick demo
python scripts/quick_start.py

# Generate YOLO dataset
python scripts/generate_dataset.py --frames 1000

# Train YOLO
python yolo_detection/train_yolo.py

# Check config
python config.py
```

---

## בהצלחה! 🚦🚗

יש שאלות? כל התיעוד נמצא בתיקייה `docs/`.

**הצעד הבא שלך**: קרא את `docs/RUNPOD_SETUP.md` והתחל את ה-Pod!
