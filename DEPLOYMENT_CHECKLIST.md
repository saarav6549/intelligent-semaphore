# 📋 Deployment Checklist - Team B

השתמש ברשימה הזו כדי לוודא שהכל מוכן לפני ה-deployment ל-RunPod.

---

## ✅ Pre-Deployment (על המחשב שלך)

### Setup בסיסי
- [ ] Python 3.10+ מותקן
- [ ] Git מותקן
- [ ] Virtual environment נוצר: `python -m venv venv`
- [ ] Dependencies מותקנים: `pip install -r requirements.txt`

### קונפיגורציה
- [ ] קראת את `config/intersection_config.yaml`
- [ ] הבנת את מבנה הנתיבים (8 lanes)
- [ ] הבנת את פאזות הרמזור (5 phases)
- [ ] בדקת תקינות: `python scripts/check_config.py`

### Git & GitHub
- [ ] Repository אתחל: `git init`
- [ ] Commit ראשון: `git add . && git commit -m "Initial setup"`
- [ ] Repository נוצר ב-GitHub
- [ ] Code pushed: `git push -u origin main`

### תיעוד
- [ ] קראת `START_HERE.md`
- [ ] קראת `docs/RUNPOD_SETUP.md`
- [ ] הבנת את ה-API: `docs/API_SPEC.md`

---

## ✅ RunPod Setup

### חשבון
- [ ] יש לך חשבון RunPod
- [ ] יש לך קרדיטים (מינימום $10 מומלץ)
- [ ] התחברת ל-dashboard

### יצירת Pod
- [ ] בחרת GPU: RTX 3090 (מומלץ) או RTX 4090
- [ ] הגדרת Storage: 50-70 GB
- [ ] Exposed ports: 2000, 8000, 6080
- [ ] Pod נוצר והפעיל

### התקנה על Pod
- [ ] התחברת ל-Web Terminal
- [ ] Clone מ-GitHub: `git clone ...`
- [ ] Docker image נבנה: `docker build ...` (30 דקות!)
- [ ] Container רץ: `docker run ...`

---

## ✅ Verification (בדיקות)

### Docker
- [ ] Container רץ: `docker ps` מראה `carla-system`
- [ ] אין שגיאות בלוגים: `docker logs carla-system`
- [ ] GPU פעיל: `nvidia-smi` מראה שימוש

### CARLA
- [ ] noVNC נפתח: `https://[pod-id]-6080.proxy.runpod.net`
- [ ] רואה את CARLA (אחרי 60 שניות המתנה)
- [ ] רכבים נוסעים בסימולציה

### API
- [ ] API Docs נפתח: `https://[pod-id]-8000.proxy.runpod.net/docs`
- [ ] Health check עובד: `/health` מחזיר `healthy`
- [ ] Config נטען: `/config` מחזיר 8 lanes, 5 phases
- [ ] Observation עובד: `/observation` מחזיר מספרים

### YOLO & Detection
- [ ] Camera stream נפתח: `https://[pod-id]-8000.proxy.runpod.net/camera/stream`
- [ ] רואה bounding boxes סביב רכבים
- [ ] רואה ROI zones צבעוניים
- [ ] המספרים הגיוניים (לא הכל 0 או הכל 100)

---

## ✅ Integration with Team A

### תקשורת
- [ ] שיתפת את ה-API URL עם Team A
- [ ] שלחת `TEAM_A_INTEGRATION.md`
- [ ] שלחת `docs/API_SPEC.md`
- [ ] תיאמתם על reward function

### Testing
- [ ] Team A הצליח להתחבר ל-API
- [ ] Team A מקבל observations תקינות
- [ ] Team A יכול לשלוח actions
- [ ] הרמזורים משתנים כשהוא שולח action

### Training
- [ ] Team A התחיל אימון PPO
- [ ] אתה עוקב ב-noVNC
- [ ] אין crashes או timeouts
- [ ] הביצועים סבירים (~10-20 FPS)

---

## ✅ Optimization (אחרי שהכל עובד)

### ROI Tuning
- [ ] הרצת `scripts/roi_calibration.py`
- [ ] כיוונת ROI zones לפי תמונה אמיתית
- [ ] עדכנת `config/intersection_config.yaml`
- [ ] בדקת שהספירה מדויקת

### YOLO Fine-tuning
- [ ] יצרת dataset: `python scripts/generate_dataset.py --frames 1000`
- [ ] אימנת YOLO: `python yolo_detection/train_yolo.py`
- [ ] Weights נשמרו: `runs/train/carla_vehicles/weights/best.pt`
- [ ] עדכנת config לשימוש ב-weights החדשים

### Performance
- [ ] FPS: 15-20 (טוב) או 10+ (מקובל)
- [ ] GPU Usage: 60-90% (אופטימלי)
- [ ] API Latency: <200ms
- [ ] אין memory leaks

---

## ✅ Documentation

### לצוות
- [ ] `TEAM_A_INTEGRATION.md` עודכן עם URL אמיתי
- [ ] `QUICK_REFERENCE.md` עודכן
- [ ] צילומי מסך של noVNC נשמרו
- [ ] צילומי מסך של camera stream נשמרו

### למסירה
- [ ] README עודכן
- [ ] יש דוגמאות בתיקייה `examples/`
- [ ] יש tests בתיקייה `tests/`
- [ ] כל הקוד מתועד (docstrings)

---

## ✅ Before Final Submission

### קוד
- [ ] כל הקוד ב-Git
- [ ] אין קבצים גדולים (models, datasets) ב-repo
- [ ] `.gitignore` עובד נכון
- [ ] הקוד רץ בלי שגיאות

### תוצאות
- [ ] יש לפחות 10 runs מוצלחים
- [ ] Team A אימן PPO בהצלחה
- [ ] יש השוואה ל-baseline
- [ ] יש גרפים של ביצועים

### תיעוד
- [ ] כל המדריכים מעודכנים
- [ ] API URL של RunPod מתועד
- [ ] יש troubleshooting guide
- [ ] יש הסברים בעברית ואנגלית

---

## 🎯 Success Criteria

המערכת מוכנה כש:

✅ **Functional**:
- CARLA רצה ויציבה על RunPod
- YOLO מזהה רכבים בדיוק >90%
- API עונה בפחות מ-200ms
- אין crashes במשך 1000+ steps

✅ **Integrated**:
- Team A מצליח לאמן PPO
- אין בעיות תקשורת
- Observations ו-Actions עובדים כהלכה

✅ **Documented**:
- Team A מבין איך להשתמש ב-API
- יש פתרונות לבעיות נפוצות
- הקוד מתועד וברור

---

## 💡 Tips

- **אל תשכח**: Stop ה-Pod כשלא עובד (חוסך כסף!)
- **Backup**: שמור weights של YOLO שאימנת (הורד מה-Pod)
- **Git**: Push changes לפני שעוצר Pod
- **Logs**: שמור logs חשובים לפני shutdown

---

## צעדים הבאים

אחרי שסימנת הכל:

1. 🎉 **אתה מוכן!**
2. 📞 תאם פגישה עם Team A
3. 🚀 התחלת אימון
4. 📊 ניתוח תוצאות
5. 📝 כתיבת דוח

**בהצלחה!** 🚦
