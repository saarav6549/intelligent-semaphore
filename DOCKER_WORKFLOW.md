# 🐳 Docker Workflow - בניה מקומית ופריסה לשרת

## 📋 סיכום התהליך

```
המחשב שלך          Docker Hub          RunPod Server
     │                   │                    │
     ├── Build ─────────►│                    │
     │   (20 דק')         │                    │
     │                   │                    │
     ├── Test ◄──────────┤                    │
     │   (5 דק')          │                    │
     │                   │                    │
     ├── Push ─────────►│                    │
     │   (15 דק')         │                    │
     │                   │                    │
     │                   ├── Pull ──────────►│
     │                   │    (10 דק')        │
     │                   │                    │
     │                   │        ┌───────────┤
     │                   │        │  Running! │
     │                   │        └───────────┘
```

**סה"כ זמן: ~50 דקות (רוב ההמתנה היא הורדות)**

---

## 🎯 למה דרך זו?

### ❌ הבעיה עם הדרך הישנה:
```bash
# על RunPod - זה נכשל!
git clone ...
bash setup_runpod.sh
# ↓ מוריד 15GB של CARLA
# ↓ נגמר המקום
# ↓ קבצים חסרים
# ↓ libApexFramework.so: cannot open shared object file
```

### ✅ הפתרון החדש:
```bash
# על המחשב שלך - יש מקום!
bash scripts/build_local.sh    # בניה מלאה
bash scripts/test_local.sh     # בדיקה
bash scripts/push_image.sh     # העלאה ל-Docker Hub

# על RunPod - רק הורדת image מוכן!
bash scripts/run_on_server.sh  # מושך ורץ
```

---

## 📦 מה תצטרך

### על המחשב שלך:
- ✅ Docker Desktop מותקן ורץ
- ✅ 30GB מקום פנוי
- ✅ חיבור אינטרנט טוב
- ✅ (אופציונלי) GPU לבדיקה מקומית

### על Docker Hub:
- ✅ חשבון חינמי (הרשמה ב-hub.docker.com)
- ✅ Image אחד חינמי (מספיק!)

### על RunPod:
- ✅ Pod עם GPU (RTX 3090 או טוב יותר)
- ✅ Ports: 2000, 8000, 6080

---

## 🚀 שלב 1: בניה מקומית

```bash
cd c:\dev\intelligent_semaphore

# בנה את ה-image (20 דקות)
bash scripts/build_local.sh
```

**מה קורה?**
1. מוריד `carlasim/carla:0.9.15` (~15GB)
2. מוסיף את הקוד שלנו
3. מתקין Python packages
4. מגדיר VNC + noVNC
5. יוצר image מוכן

**Output מצופה:**
```
✅ Build Complete!
Image size: 16.2GB
```

---

## 🧪 שלב 2: בדיקה מקומית

```bash
# הרץ בדיקה מקומית (5 דקות)
bash scripts/test_local.sh
```

**מה קורה?**
1. מפעיל container מקומי
2. מתחיל CARLA + API + VNC
3. מציג logs

**בדוק:**
- 🌐 פתח: http://localhost:6080 (noVNC)
- 📝 פתח: http://localhost:8000/docs (API)
- ✅ אמור לראות CARLA רץ!

**אם זה עובד → המשך!**

---

## 📤 שלב 3: העלאה ל-Docker Hub

```bash
# דחוף ל-Docker Hub (15 דקות)
bash scripts/push_image.sh
```

**זה ישאל:**
```
Enter your Docker Hub username: <YOUR_USERNAME>
Username: <YOUR_USERNAME>
Password: <YOUR_PASSWORD>
```

**מה קורה?**
1. תיוג ה-image
2. התחברות ל-Docker Hub
3. העלאת ה-image (15GB)

**Output מצופה:**
```
✅ Push Complete!
Your image is now available at:
  docker pull <YOUR_USERNAME>/intelligent-traffic-teamb:latest
```

**💾 שמור את השם הזה!** תצטרך אותו בשרת.

---

## ☁️ שלב 4: הרצה על RunPod

### 4.1 צור Pod ב-RunPod

1. לך ל-[runpod.io](https://runpod.io)
2. **Deploy** → **GPU Pods**
3. **בחר GPU:** RTX 3090 (או טוב יותר)
4. **Expose Ports:** `2000, 8000, 6080`
5. **Deploy!**

### 4.2 התחבר ל-Terminal

בתוך RunPod Web Terminal:

```bash
# התקן Docker אם צריך
apt-get update && apt-get install -y docker.io

# התקן NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update && apt-get install -y nvidia-docker2
systemctl restart docker

# בדוק GPU
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### 4.3 שלוף והרץ את ה-Image שלך

```bash
# שלוף והרץ (10 דקות)
docker pull <YOUR_USERNAME>/intelligent-traffic-teamb:latest

docker run -d \
    --name carla-system \
    --gpus all \
    --restart unless-stopped \
    -p 2000:2000 \
    -p 8000:8000 \
    -p 6080:6080 \
    <YOUR_USERNAME>/intelligent-traffic-teamb:latest

# המתן ובדוק logs
sleep 40
docker logs -f carla-system
```

### 4.4 גש למערכת

קבל את ה-Pod ID מ-RunPod Dashboard, אז:

**noVNC (ראה את CARLA):**
```
https://[pod-id]-6080.proxy.runpod.net
```

**API (חיבור ל-Team A):**
```
https://[pod-id]-8000.proxy.runpod.net/docs
```

---

## ✅ אימות שהכל עובד

### 1. בדוק Logs:
```bash
docker logs carla-system
```

**חפש:**
```
✓ CARLA server started
✓ API server started
✓ All services started successfully!
```

### 2. בדוק noVNC:
- פתח את ה-URL
- אמור לראות חלון CARLA
- (אולי שחור, זה OK אם אין סימולציה רצה)

### 3. בדוק API:
- פתח `/docs`
- נסה: `GET /health`
- Response: `{"status": "healthy"}`

### 4. נסה reset:
```bash
# ב-API docs או curl:
POST /reset
```

**צריך להחזיר:**
```json
{
  "status": "success",
  "message": "Environment reset"
}
```

---

## 🎊 סיימת! עכשיו תן ל-Team A

```bash
# שלח ל-Team A:
API_URL="https://[pod-id]-8000.proxy.runpod.net"
```

**תן לו גם:**
1. `docs/API_SPEC.md`
2. `TEAM_A_INTEGRATION.md`

**הוא יכול להתחיל לאמן!** 🚀

---

## 📝 Commands מועילים

### על השרת:
```bash
# ראה logs
docker logs -f carla-system

# אתחל
docker restart carla-system

# עצור
docker stop carla-system

# התחל מחדש
docker start carla-system

# הסר והרץ מחדש
docker rm -f carla-system
docker run -d --name carla-system --gpus all \
  -p 2000:2000 -p 8000:8000 -p 6080:6080 \
  <YOUR_USERNAME>/intelligent-traffic-teamb:latest
```

### עדכון Image:
```bash
# על המחשב שלך
bash scripts/build_local.sh
bash scripts/push_image.sh

# על השרת
docker pull <YOUR_USERNAME>/intelligent-traffic-teamb:latest
docker restart carla-system
```

---

## 🐛 Troubleshooting

### שגיאה: "Cannot connect to Docker daemon"
```bash
# הפעל Docker
systemctl start docker
systemctl enable docker
```

### שגיאה: "NVIDIA not found"
```bash
# התקן nvidia-docker2
apt-get install -y nvidia-docker2
systemctl restart docker
```

### Container מת מיד
```bash
# ראה למה
docker logs carla-system
```

### CARLA לא מתחיל
```bash
# בדוק GPU
docker exec carla-system nvidia-smi

# בדוק processes
docker exec carla-system ps aux | grep Carla
```

### Port כבר בשימוש
```bash
# מצא מי משתמש
netstat -tlnp | grep 2000

# הרוג process
kill -9 <PID>
```

---

## 💰 עלויות

| שלב | זמן | עלות (RTX 3090 @ $0.34/hr) |
|-----|-----|---------------------------|
| Build מקומי | 20 דק' | $0 (מחשב שלך) |
| Test מקומי | 5 דק' | $0 (מחשב שלך) |
| Push | 15 דק' | $0 (רשת) |
| Pull בשרת | 10 דק' | $0.06 |
| הרצה 10 שעות | 10 שעות | $3.40 |
| **סה"כ setup** | **50 דק'** | **$0.06** |

**💡 Tip:** עצור את ה-Pod כשלא עובד!

---

## 🔄 Workflow קבוע

```bash
# כשמעדכנים קוד:
1. ערוך קבצים
2. bash scripts/build_local.sh
3. bash scripts/test_local.sh
4. bash scripts/push_image.sh
5. SSH לשרת: docker pull + restart

# כשמשנים Pod:
1. צור Pod חדש
2. bash scripts/run_on_server.sh <username>
3. עדכן URLs ל-Team A
```

---

## 🎓 למה זה עובד?

### הבעיה הישנה:
- RunPod Pod = מקום מוגבל (50GB default)
- CARLA base image = 15GB
- בניית image = עוד 5GB temp files
- **נגמר המקום באמצע!**

### הפתרון החדש:
- בונים **במחשב שלך** (הרבה מקום)
- מעלים **image מוכן** ל-Docker Hub
- שולפים **image שלם** ל-RunPod
- **אין בעיות מקום!**

---

**🎉 מוכן להתחיל? ראה את השלבים למעלה!**
