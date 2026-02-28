# 🎯 התחלה מהירה - 10 דקות

## אתה כאן כי אתה Team B וצריך להתחיל מהר!

---

## תרחיש 1: יש לי Windows ורוצה רק ל-Deploy

### צעד 1: Setup (3 דקות)
```powershell
cd c:\dev\intelligent_semaphore
.\scripts\setup_windows.ps1
```

### צעד 2: Git (2 דקות)
```powershell
git add .
git commit -m "Team B initial setup"
# צור repo ב-github.com
git remote add origin https://github.com/[YOU]/intelligent-semaphore.git
git push -u origin main
```

### צעד 3: RunPod (5 דקות + 30 דקות המתנה)
1. לך ל-[runpod.io](https://runpod.io)
2. Deploy > GPU Pods > בחר RTX 3090
3. Ports: 2000, 8000, 6080
4. Deploy

### צעד 4: בתוך RunPod Terminal
```bash
git clone https://github.com/[YOU]/intelligent-semaphore.git
cd intelligent-semaphore
bash scripts/setup_runpod.sh  # 30 דקות!
```

### צעד 5: הרץ
```bash
docker run -d --name carla-system --gpus all \
  -p 2000:2000 -p 8000:8000 -p 6080:6080 \
  -v $(pwd):/workspace carla-vision-system:latest

docker logs -f carla-system
```

### צעד 6: גש
- noVNC: `https://[pod-id]-6080.proxy.runpod.net`
- API: `https://[pod-id]-8000.proxy.runpod.net/docs`

**סיימת!** תן את ה-API URL ל-Team A.

---

## תרחיש 2: רוצה להבין מה קורה קודם

קרא בסדר הזה:
1. `START_HERE.md` (5 דקות)
2. `docs/RUNPOD_SETUP.md` (10 דקות)
3. `PROJECT_SUMMARY.md` (5 דקות)
4. `docs/API_SPEC.md` (5 דקות)

אחר כך עקוב אחרי התרחיש הראשון למעלה.

---

## תרחיש 3: Team A רוצה להתחיל עכשיו

תן לו:
1. את ה-URL: `https://[pod-id]-8000.proxy.runpod.net`
2. את הקובץ: `TEAM_A_INTEGRATION.md`
3. את הקובץ: `docs/API_SPEC.md`

הוא יכול להתחיל מיד!

---

## Commands מהירים

```powershell
# על Windows
.\scripts\setup_windows.ps1          # Setup
python scripts\check_config.py       # בדוק config
python scripts\test_system.py        # בדוק הכל (דורש CARLA local)

# על RunPod
bash scripts/setup_runpod.sh         # Setup מלא
docker logs -f carla-system          # ראה logs
docker restart carla-system          # אתחל
bash scripts/stop_runpod.sh          # עצור בטוח
```

---

## URLs חשובים

| מה | איפה |
|----|------|
| RunPod | https://runpod.io |
| CARLA Docs | https://carla.readthedocs.io |
| YOLO Docs | https://docs.ultralytics.com |
| FastAPI Docs | https://fastapi.tiangolo.com |

---

## עזרה

**לא עובד?** → `docs/TROUBLESHOOTING.md`  
**שאלות על RunPod?** → `docs/RUNPOD_SETUP.md`  
**Team A שואל?** → `docs/API_SPEC.md`

---

**בהצלחה! זמן לעשות קסמים! ✨🚦**
