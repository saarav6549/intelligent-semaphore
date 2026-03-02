# 🚀 Simple Deploy - Build on Server

## למה זה טוב יותר?

```
❌ הדרך הישנה:
  מחשב שלך → build 46GB → push 46GB → RunPod pull 46GB
  ⏱️  זמן: ~2 שעות להעברת נתונים

✅ הדרך החדשה:
  מחשב שלך → push קוד (5MB) → RunPod build מקומית
  ⏱️  זמן: ~20 דקות (הורדות ישירות מהמקור)
```

---

## 📝 3 שלבים פשוטים

### 1️⃣ העלה לGitHub (3 דקות)

**על Windows:**

```powershell
cd c:\dev\intelligent_semaphore

# אתחול Git (אם לא עשית)
git init
git add .
git commit -m "Initial commit - Team B intelligent semaphore"

# צור repo ב-GitHub.com (דרך הדפדפן)
# אז חבר אותו:
git remote add origin https://github.com/[YOUR_USERNAME]/intelligent-semaphore.git
git branch -M main
git push -u origin main
```

**או אם הrepo כבר קיים:**

```powershell
git add .
git commit -m "Updated Docker setup for server build"
git push
```

---

### 2️⃣ Setup RunPod (5 דקות)

1. לך ל-[runpod.io](https://runpod.io)
2. **Deploy** → **GPU Pods**
3. בחר **RTX 3090** (או טוב יותר)
4. **Expose Ports:** `2000, 8000, 6080`
5. לחץ **Deploy**

---

### 3️⃣ Build על RunPod (20 דקות)

**ב-RunPod Web Terminal:**

```bash
# Clone הrepo שלך
git clone https://github.com/[YOUR_USERNAME]/intelligent-semaphore.git
cd intelligent-semaphore

# Run setup (זה יבנה הכל על השרת!)
bash scripts/setup_runpod_simple.sh
```

**המתן ~20 דקות בזמן ש:**
- מוריד CARLA (~15GB)
- מתקין Python packages
- בונה את ה-image

**אז הרץ:**

```bash
docker run -d \
    --name carla-system \
    --gpus all \
    -e NVIDIA_VISIBLE_DEVICES=all \
    -e NVIDIA_DRIVER_CAPABILITIES=all \
    --restart unless-stopped \
    -p 2000:2000 \
    -p 8000:8000 \
    -p 6080:6080 \
    intelligent-traffic-teamb:latest

# בדוק logs
docker logs -f carla-system
```

---

## ✅ Alternative: RunPod WITHOUT docker (no Docker-in-Docker)

Some RunPod templates are already “a container”, and **do not include the `docker` CLI/daemon**.
In that case, you can still run everything by using a **CARLA-based pod image** and installing the repo dependencies directly.

### Step A: Create the Pod with a CARLA base image
- Recommended: use a root-enabled CARLA image so `apt-get` works:
  - Build/push once (from your machine): `docker/Dockerfile.carla_root` → `saarav/carla-root:0.9.15`
  - Then set the Pod container image to `saarav/carla-root:0.9.15`

- If you already have root access on your pod, you can also use:
  - `carlasim/carla:0.9.15` (contains `/home/carla/CarlaUE4.sh`)
- Expose ports: `2000, 8000, 6080` (optional: `5900`)

### Step B: Use tmux so SSH disconnects won’t stop the setup

```bash
apt-get update && apt-get install -y tmux
tmux new -s setup
```

### Step C: Clone + run the no-docker setup script

```bash
git clone https://github.com/[YOUR_USERNAME]/intelligent-semaphore.git
cd intelligent-semaphore
bash scripts/runpod_no_docker.sh
```

If your SSH disconnects, reconnect and run:

```bash
tmux attach -t setup
```

---

## 🌐 גש למערכת

קבל את ה-Pod ID מ-RunPod dashboard, אז:

**noVNC (ראה CARLA):**
```
https://[pod-id]-6080.proxy.runpod.net
```

**API (ל-Team A):**
```
https://[pod-id]-8000.proxy.runpod.net/docs
```

---

## 🎊 זהו! סיימת!

**עכשיו תן ל-Team A את ה-API URL!**

---

## 🔄 עדכונים בעתיד

כשמשנים קוד:

```bash
# על המחשב שלך
git add .
git commit -m "Updated code"
git push

# על RunPod
cd intelligent-semaphore
git pull
docker stop carla-system
docker rm carla-system
docker build -t intelligent-traffic-teamb:latest -f docker/Dockerfile .
docker run -d --name carla-system --gpus all \
  -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=all \
  --restart unless-stopped \
  -p 2000:2000 -p 8000:8000 -p 6080:6080 \
  intelligent-traffic-teamb:latest
```

---

## 💰 עלויות

| פעולה | זמן | עלות (RTX 3090 @ $0.34/hr) |
|-------|-----|---------------------------|
| Build על שרת | 20 דק' | $0.11 |
| הרצה 10 שעות | 10 שעות | $3.40 |
| **סה"כ** | | **$3.51** |

**לעומת העברת 46GB:** זמן + bandwidth + כאב ראש 😅

---

## ❓ שאלות נפוצות

**ש: למה לא לבנות על המחשב שלי?**  
ת: אפשר! אבל להעביר 46GB זה איטי. בניה על השרת מהירה יותר.

**ש: האם זה בטוח?**  
ת: כן! השרת מוריד ישירות מהמקורות הרשמיים (Docker Hub, PyPI).

**ש: מה אם הבנייה נכשלת?**  
ת: ראה logs: `docker logs <container-id>` או פתח issue.

**ש: כמה זמן זה לוקח?**  
ת: ~20 דקות לבנייה + 2 דקות הרצה = 22 דקות סה"כ

---

**🎉 זה הכל! הרבה יותר פשוט מהדרך הישנה!**
