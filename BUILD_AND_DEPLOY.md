# 🚀 Build & Deploy - TL;DR

## הבעיה שפתרנו

```
❌ הדרך הישנה (לא עובדת):
RunPod → git clone → bash setup_runpod.sh
         ↓
      נגמר המקום
         ↓
    libApexFramework.so: not found
         ↓
       💥 FAIL
```

```
✅ הדרך החדשה (עובדת):
מחשב שלך → Build → Push → RunPod → Pull → ✅ SUCCESS!
```

---

## 4 צעדים פשוטים

### 1️⃣ בנה מקומית (20 דקות)

**Windows:**
```powershell
cd c:\dev\intelligent_semaphore
.\scripts\build_local.ps1
```

**Linux/Mac:**
```bash
cd c:\dev\intelligent_semaphore
bash scripts/build_local.sh
```

**מה קורה:** מוריד CARLA + בונה image שלם

---

### 2️⃣ בדוק שעובד (5 דקות)

**Windows:**
```powershell
.\scripts\test_local.ps1
```

**Linux/Mac:**
```bash
bash scripts/test_local.sh
```

**בדוק:** http://localhost:6080 (צריך לראות CARLA!)

---

### 3️⃣ העלה ל-Docker Hub (15 דקות)

**Windows:**
```powershell
.\scripts\push_image.ps1
```

**Linux/Mac:**
```bash
bash scripts/push_image.sh
```

**תצטרך:** חשבון Docker Hub (חינמי!)

---

### 4️⃣ הרץ על RunPod (10 דקות)

1. **צור Pod:** RTX 3090, Ports: `2000, 8000, 6080`

2. **ב-RunPod Terminal:**

```bash
# התקן Docker + NVIDIA (פעם אחת)
apt-get update && apt-get install -y docker.io

distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update && apt-get install -y nvidia-docker2
systemctl restart docker

# שלוף והרץ את ה-image שלך
docker pull <YOUR_USERNAME>/intelligent-traffic-teamb:latest

docker run -d \
    --name carla-system \
    --gpus all \
    --restart unless-stopped \
    -p 2000:2000 \
    -p 8000:8000 \
    -p 6080:6080 \
    <YOUR_USERNAME>/intelligent-traffic-teamb:latest

# בדוק logs
docker logs -f carla-system
```

3. **גש למערכת:**
   - **noVNC:** `https://[pod-id]-6080.proxy.runpod.net`
   - **API:** `https://[pod-id]-8000.proxy.runpod.net/docs`

---

## ✅ זהו! סיימת!

תן ל-Team A את ה-API URL ושניכם יכולים להתחיל לעבוד! 🎉

---

## 📚 למידע מפורט

- **מדריך מלא:** `DOCKER_WORKFLOW.md`
- **API Docs:** `docs/API_SPEC.md`
- **ל-Team A:** `TEAM_A_INTEGRATION.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`

---

## 💡 Tips

**עדכון קוד:**
```bash
# על המחשב שלך
.\scripts\build_local.ps1
.\scripts\push_image.ps1

# על RunPod
docker pull <USERNAME>/intelligent-traffic-teamb:latest
docker restart carla-system
```

**בדיקת בריאות:**
```bash
# Logs
docker logs -f carla-system

# Health check
curl http://localhost:8000/health
```

**עצירת Pod (חיסכון בכסף!):**
```bash
# ב-RunPod Dashboard:
Stop Pod → Save $$$
```

---

## 🐛 בעיות נפוצות

**Docker לא רץ:**
```powershell
# הפעל Docker Desktop
```

**חסר מקום:**
```powershell
# נקה images ישנים
docker system prune -a
```

**Port תפוס:**
```bash
# בדוק מי משתמש
netstat -ano | findstr :2000
# הרוג process
taskkill /PID <PID> /F
```

---

**🎊 בהצלחה!**
