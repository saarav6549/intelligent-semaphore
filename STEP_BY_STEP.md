# 👣 צעד אחר צעד - מאפס עד לעבודה על RunPod

## Timeline: 2-3 שעות (כולל המתנות)

---

## שלב 1️⃣: הכנת המחשב שלך (10 דקות)

### מה צריך:
- ✅ Python 3.10+
- ✅ Git
- ✅ חשבון GitHub

### איך:

**1. בדוק אם Python מותקן:**
```powershell
python --version
```
אם לא → הורד מ-[python.org](https://python.org)

**2. בדוק אם Git מותקן:**
```powershell
git --version
```
אם לא → הורד מ-[git-scm.com](https://git-scm.com)

**3. הכנת הפרויקט:**
```powershell
cd c:\dev\intelligent_semaphore
.\scripts\setup_windows.ps1
```

זה יתקין את כל ה-dependencies.

✅ **Checkpoint**: אמור להיות לך venv עם כל החבילות מותקנות.

---

## שלב 2️⃣: העלאה ל-GitHub (5 דקות)

### 1. צור Repository

1. לך ל-[github.com](https://github.com)
2. לחץ **"New repository"**
3. שם: `intelligent-semaphore`
4. Private או Public (לבחירתך)
5. **אל תסמן** "Initialize with README"
6. לחץ **"Create repository"**

### 2. העלה את הקוד

```powershell
cd c:\dev\intelligent_semaphore

git init
git add .
git commit -m "Team B initial setup - Vision system"
git branch -M main
git remote add origin https://github.com/[YOUR_USERNAME]/intelligent-semaphore.git
git push -u origin main
```

✅ **Checkpoint**: הקוד שלך ב-GitHub. רענן את העמוד ותראה את כל הקבצים.

---

## שלב 3️⃣: הרשמה ל-RunPod (5 דקות)

### 1. צור חשבון

1. לך ל-[runpod.io](https://runpod.io)
2. לחץ **"Sign Up"**
3. הירשם עם Google/GitHub או Email
4. אמת email

### 2. הוסף קרדיט

1. לחץ על שמך בפינה ימנית עליונה
2. **"Billing"**
3. **"Add Credit"**
4. הוסף לפחות **$10** (מספיק לכמה ימי עבודה)

✅ **Checkpoint**: יש לך יתרה ב-RunPod dashboard.

---

## שלב 4️⃣: יצירת Pod (10 דקות)

### 1. בחירת GPU

1. לחץ **"Deploy"** בתפריט העליון
2. בחר **"GPU Pods"**
3. תראה טבלה של GPUs זמינים

**המלצה שלי**: RTX 3090 (24GB)
- מחיר: ~$0.34/hour
- מספיק חזק ל-CARLA + YOLO
- לא יקר מדי

4. לחץ **"Deploy"** ליד RTX 3090

### 2. הגדרת Pod

**Container Disk**: `30 GB` (מספיק! אם תאמן YOLO שים 40GB)

**Expose HTTP Ports**: לחץ "+ Add Port" 3 פעמים:
- `2000`
- `8000`
- `6080` ← **זה החשוב ביותר!**

**Container Image**: `nvidia/cuda:12.1.0-devel-ubuntu22.04`

**Volume**: (אופציונלי) 20GB אם רוצה לשמור נתונים

5. לחץ **"Deploy On-Demand"** (או "Deploy Spot" לחיסכון)

### 3. המתן

המערכת תקים את ה-Pod (30-60 שניות).

✅ **Checkpoint**: רואה את ה-Pod שלך ברשימת "My Pods" עם סטטוס "Running".

---

## שלב 5️⃣: גישה ל-Pod (5 דקות)

### 1. פתח Terminal

לחץ על שם ה-Pod → כפתור **"Connect"** → **"Start Web Terminal"**

יפתח לך terminal בדפדפן.

### 2. Clone הקוד

```bash
cd /workspace
git clone https://github.com/[YOUR_USERNAME]/intelligent-semaphore.git
cd intelligent-semaphore
ls -la
```

אמור לראות את כל הקבצים שלך!

✅ **Checkpoint**: הקוד על ה-Pod.

---

## שלב 6️⃣: Build Docker Image (40 דקות)

### הרץ את הפקודה הזו:

```bash
docker build -t carla-vision-system:latest -f docker/Dockerfile .
```

**זה ייקח 30-40 דקות!** 

למה? כי זה:
- מוריד CARLA (8GB)
- מוריד YOLO weights
- מתקין כל ה-dependencies

**טיפ**: לך להכין קפה ☕

### בדוק שהבנייה הצליחה:

```bash
docker images | grep carla-vision-system
```

אמור לראות שורה עם ה-image שלך.

✅ **Checkpoint**: Docker image נבנה בהצלחה.

---

## שלב 7️⃣: הרצת המערכת (5 דקות)

### 1. הרץ את ה-Container

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

### 2. עקוב אחרי ההפעלה

```bash
docker logs -f carla-system
```

תראה:
```
Starting virtual display...
Starting VNC server...
Starting CARLA server...
Waiting for CARLA to start (30 seconds)...
```

**המתן 60 שניות** עד שתראה:
```
All services started successfully!
```

### 3. בדוק שהכל רץ

```bash
docker ps
```

אמור לראות `carla-system` עם status "Up".

✅ **Checkpoint**: Container רץ והכל עולה.

---

## שלב 8️⃣: הרגע הגדול - ראה את CARLA! (2 דקות)

### 1. מצא את ה-URLs

ב-RunPod Dashboard:
1. לך ל-Pod שלך
2. גלול ל-**"TCP Port Mappings"**
3. תראה טבלה:

```
6080 → https://xxxxx-6080.proxy.runpod.net
8000 → https://xxxxx-8000.proxy.runpod.net
```

**העתק את שני ה-URLs האלה!**

### 2. פתח noVNC

1. פתח דפדפן (Chrome/Firefox)
2. עבור ל: `https://xxxxx-6080.proxy.runpod.net`
3. לחץ **"Connect"**
4. **חכה 30 שניות**
5. 🎉 **תראה את CARLA עם רכבים נוסעים!**

### 3. פתח API Docs

1. עבור ל: `https://xxxxx-8000.proxy.runpod.net/docs`
2. תראה Swagger UI עם כל ה-endpoints
3. נסה להריץ **GET /health** - לחץ "Try it out" → "Execute"

✅ **Checkpoint**: רואה CARLA בדפדפן, API עובד!

---

## שלב 9️⃣: בדיקה מהירה (3 דקות)

### ב-API Docs (Swagger UI):

**1. GET /config**
- לחץ "Try it out" → "Execute"
- תראה: 8 lanes, 5 phases

**2. GET /observation**
- לחץ "Try it out" → "Execute"
- תראה: `{"observation": [0.15, 0.25, ...], "raw_counts": [3, 5, ...]}`

**3. GET /camera/stream**
- פתח בטאב חדש: `https://xxxxx-8000.proxy.runpod.net/camera/stream`
- תראה: מצלמה חיה עם bounding boxes סביב רכבים!

**4. POST /action**
- נסה לשלוח action: `{"action": 2}`
- ברוב noVNC תראה את הרמזורים משתנים!

✅ **Checkpoint**: כל ה-endpoints עובדים, רואה detections!

---

## שלב 🔟: שיתוף עם Team A (2 דקות)

### שלח לו:

**Email/Message Template:**

```
היי [Team A],

המערכת שלי מוכנה! 🎉

API URL:
https://xxxxx-8000.proxy.runpod.net

קבצים שתצטרך:
1. TEAM_A_INTEGRATION.md - המדריך שלך
2. docs/API_SPEC.md - מפרט API מלא
3. examples/team_a_example.py - קוד לדוגמה

Observation: 8 floats (normalized vehicle counts)
Action: integer 0-4 (traffic phase)

תוכל לראות את הסימולציה בזמן אמת:
https://xxxxx-6080.proxy.runpod.net

Camera feed עם detections:
https://xxxxx-8000.proxy.runpod.net/camera/stream

אני פה אם צריך עזרה!
```

✅ **Checkpoint**: Team A יכול להתחיל לעבוד!

---

## 🎉 סיימת!

### מה השגת:

✅ מערכת vision מלאה על GPU בענן  
✅ API שעובד ונגיש  
✅ ויזואליזציה של CARLA בזמן אמת  
✅ כל התיעוד והדוגמאות  
✅ Team A יכול להתחיל אימון  

### מה הלאה:

**השבוע:**
- עקוב אחרי האימון של Team A
- תקן bugs שמופיעים
- כוונן ROI zones אם צריך

**בעתיד:**
- אמן YOLO custom (אופציונלי)
- אופטימיזציה
- תוצאות ודוח

---

## ⏱️ Time Breakdown (סה"ך: ~2 שעות + המתנות)

| שלב | זמן עבודה | זמן המתנה | סה"ך |
|-----|-----------|-----------|------|
| 1. Setup Windows | 5 דקות | 5 דקות (הורדות) | 10 דקות |
| 2. GitHub | 5 דקות | - | 5 דקות |
| 3. RunPod signup | 5 דקות | - | 5 דקות |
| 4. Create Pod | 10 דקות | 1 דקה | 11 דקות |
| 5. Access Pod | 5 דקות | - | 5 דקות |
| 6. Build Docker | 5 דקות | 30-40 דקות | 40 דקות |
| 7. Run system | 5 דקות | 1 דקה | 6 דקות |
| 8. View CARLA | 2 דקות | 30 שניות | 3 דקות |
| 9. Test API | 3 דקות | - | 3 דקות |
| 10. Share with A | 2 דקות | - | 2 דקות |
| **סה"ך** | **47 דקות** | **37 דקות** | **~90 דקות** |

---

## 💰 Cost Breakdown

**Setup phase** (שלבים 1-10):
- Build Docker: 40 דקות = $0.23
- Testing: 20 דקות = $0.11
- **סה"ך**: ~$0.35

**זה בערך מחיר כוס קפה!** ☕

---

## 🆘 במידה ונתקעת

| איפה נתקעת | מה לעשות |
|------------|----------|
| שלב 1 | קרא `docs/WINDOWS_SETUP.md` |
| שלב 2 | Google: "git push to github" |
| שלב 3-5 | קרא `docs/RUNPOD_SETUP.md` |
| שלב 6-7 | בדוק `docker logs carla-system` |
| שלב 8-9 | קרא `docs/TROUBLESHOOTING.md` |

**כלל זהב**: תמיד תבדוק logs קודם!

---

## 📸 Screenshots שכדאי לשמור

1. ✅ RunPod Pod running
2. ✅ noVNC showing CARLA
3. ✅ API Swagger UI
4. ✅ Camera stream with detections
5. ✅ Terminal showing successful logs

אלו תצטרך למצגת/דוח!

---

## ✍️ Notes לעצמך

תעדכן אחרי שסיימת:

```
Pod ID שלי: _________________
API URL: https://____________-8000.proxy.runpod.net
noVNC URL: https://____________-6080.proxy.runpod.net

תאריך התחלה: ___/___/2026
זמן בנייה: _____ דקות
בעיות שפגשתי: 
_________________________________
_________________________________

GPU שבחרתי: RTX ______
עלות שעתית: $______
```

---

## 🎯 Success Criteria

אתה יודע שהצלחת כש:

✅ רואה CARLA רצה ב-noVNC  
✅ API מחזיר observations תקינות  
✅ Camera stream מראה bounding boxes  
✅ אין שגיאות ב-logs  
✅ Team A יכול להתחבר ל-API  

אם כל אלה ✅ - **מזל טוב! סיימת את החלק הקשה!** 🎉

---

## צעדים הבאים (לא דחוף)

### אופציונלי אבל מומלץ:

**1. כיול ROI (30-60 דקות)**
```bash
python scripts/roi_calibration.py --carla
```
זה ישפר את דיוק ספירת הרכבים.

**2. Fine-tune YOLO (2-3 שעות)**
```bash
# Generate dataset
python scripts/generate_dataset.py --frames 1000

# Train model
python yolo_detection/train_yolo.py --epochs 100
```
זה ישפר את דיוק הזיהוי ל-95%+.

**3. Stress Test**
```bash
# Run for 1000 steps
python examples/team_a_example.py --demo random
```
ודא שהמערכת יציבה לאורך זמן.

---

## 🏁 הגעת לסוף!

**עכשיו**:
1. המערכת שלך רצה על GPU בענן ✅
2. אתה יכול לראות אותה בדפדפן ✅
3. ה-API שלך זמין ל-Team A ✅

**הלאה**:
- Team A מאמן PPO
- אתה עוקב ומתקן
- ביחד משיגים תוצאות מעולות

**בהצלחה רבה! 🚀🚦🤖**

---

## Shortcuts לשלבים הבאים

```bash
# Stop Pod when done working (IMPORTANT!)
docker stop carla-system
# Then: RunPod Dashboard → Stop Pod

# Resume next day
# RunPod Dashboard → Start Pod
docker start carla-system
docker logs -f carla-system

# Update code
git pull
docker restart carla-system

# Monitor GPU
nvidia-smi -l 1

# Check if everything works
python scripts/test_system.py
```

---

**תזכורת**: Stop את ה-Pod כשלא עובד! 💸
