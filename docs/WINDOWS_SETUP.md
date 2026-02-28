# הכנת סביבת העבודה ב-Windows

מדריך זה מסביר איך להכין את המחשב Windows שלך לעבודה עם הפרויקט.

## מה אתה צריך

1. **Git** - לניהול קוד
2. **Python 3.10+** - להרצת סקריפטים
3. **VS Code / Cursor** - עורך קוד
4. **Docker Desktop** (אופציונלי) - לבדיקות מקומיות
5. **חשבון GitHub** - לשיתוף קוד

---

## התקנת Python

### 1. הורדה והתקנה

1. לך ל-[python.org/downloads](https://www.python.org/downloads/)
2. הורד **Python 3.10** או יותר חדש
3. בהתקנה: **סמן "Add Python to PATH"** ✅
4. לחץ "Install Now"

### 2. בדיקה

פתח PowerShell והרץ:
```powershell
python --version
```

אמור לראות: `Python 3.10.x` או יותר.

---

## התקנת Git

### 1. הורדה

1. לך ל-[git-scm.com](https://git-scm.com/download/win)
2. הורד והתקן
3. בהתקנה: השאר את כל ברירות המחדל

### 2. הגדרה ראשונית

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## התקנת Dependencies

### בתיקיית הפרויקט

```powershell
cd c:\dev\intelligent_semaphore

# צור virtual environment
python -m venv venv

# הפעל אותו
.\venv\Scripts\Activate.ps1

# התקן packages
pip install -r requirements.txt
```

**הערה**: אם מקבל שגיאת "cannot be loaded because running scripts is disabled":
```powershell
# הרץ את זה כ-Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## התקנת Docker Desktop (אופציונלי)

לבדיקות מקומיות בלבד. לא חובה כי המערכת תרוץ ב-RunPod.

### 1. הורדה

1. לך ל-[docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. הורד Docker Desktop for Windows
3. התקן והפעל מחדש את המחשב

### 2. הפעלה

1. פתח Docker Desktop
2. ודא שה-Docker demon רץ (סמל ירוק למטה)

### 3. WSL 2 (נדרש)

Docker Desktop משתמש ב-WSL 2. אם צריך להתקין:
```powershell
# הרץ כ-Administrator
wsl --install
```

---

## כלים מומלצים

### 1. Windows Terminal (מומלץ מאוד!)

- הורד מ-Microsoft Store
- הרבה יותר נוח מ-PowerShell הרגיל
- תומך בטאבים וצבעים

### 2. Visual Studio Code או Cursor

אתה כבר משתמש ב-Cursor - מעולה!

### 3. VNC Viewer (אופציונלי)

אם אתה מעדיף VNC client מקצועי על noVNC:
- הורד [TigerVNC](https://tigervnc.org/) או [RealVNC](https://www.realvnc.com/)
- התחבר ל: `[runpod-ip]:[vnc-port]`

---

## הגדרת GitHub

### 1. יצירת Repository

1. לך ל-[github.com](https://github.com)
2. לחץ **"New repository"**
3. שם: `intelligent-semaphore`
4. סוג: **Private** (אם לא רוצה שיהיה פומבי)
5. לחץ **"Create repository"**

### 2. העלאת הקוד

```powershell
cd c:\dev\intelligent_semaphore

git init
git add .
git commit -m "Initial commit - Team B vision system"
git remote add origin https://github.com/[USERNAME]/intelligent-semaphore.git
git branch -M main
git push -u origin main
```

### 3. משיכת הקוד ב-RunPod

```bash
# ב-RunPod Terminal:
cd /workspace
git clone https://github.com/[USERNAME]/intelligent-semaphore.git
cd intelligent-semaphore
```

---

## בדיקה מהירה שהכל עובד

### בדוק Python

```powershell
python --version
pip --version
```

### בדוק Git

```powershell
git --version
```

### בדוק Dependencies

```powershell
cd c:\dev\intelligent_semaphore
.\venv\Scripts\Activate.ps1
python -c "import torch; import ultralytics; print('OK')"
```

**אם מקבל שגיאות**:
```powershell
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

---

## עבודה עם RunPod מ-Windows

### העתקת קבצים ל/מ-RunPod

**דרך 1: Git** (מומלץ)
```powershell
# על Windows
git add .
git commit -m "Update"
git push

# ב-RunPod
git pull
```

**דרך 2: RunPod File Manager**
- בממשק RunPod: לחצן "Files"
- גרור ושחרר קבצים

**דרך 3: SCP** (מתקדם)
```powershell
scp -P [port] file.txt root@[pod-id].ssh.runpod.io:/workspace/
```

---

## טיפים ל-PowerShell

### aliases שימושיים

הוסף לפרופיל שלך (`notepad $PROFILE`):

```powershell
function dc { docker-compose $args }
function dps { docker ps $args }
function dlogs { docker logs -f $args }

function activate { .\venv\Scripts\Activate.ps1 }
```

שמור וסגור. עכשיו תוכל להקליד `activate` במקום `.\venv\Scripts\Activate.ps1`.

---

## הכנה לעבודה עם חבר צוות A

### שיתוף הגדרות

צור קובץ `TEAM_A_README.md`:

```markdown
# Team A Integration Guide

## API Endpoint
https://xxxxx-8000.proxy.runpod.net

## Observation Space
- Shape: (8,)
- Type: float32
- Range: [0.0, 1.0]
- Meaning: Normalized vehicle counts per lane

## Action Space
- Type: Discrete
- Range: [0, 4]
- Meaning: Traffic light phase ID

## Example Code
See docs/API_SPEC.md

## Contact
[Your contact info]
```

---

## סיכום Checklist

לפני שמתחילים:

- [ ] Python 3.10+ מותקן
- [ ] Git מותקן
- [ ] תיקיית הפרויקט: `c:\dev\intelligent_semaphore`
- [ ] Dependencies מותקנים: `pip install -r requirements.txt`
- [ ] יש לך חשבון GitHub
- [ ] יש לך חשבון RunPod עם קרדיטים
- [ ] קראת את `docs/RUNPOD_SETUP.md`

אם סימנת את הכל - אתה מוכן! 🚀

---

## עזרה נוספת

- **Python**: [docs.python.org](https://docs.python.org/3/)
- **Git**: [git-scm.com/doc](https://git-scm.com/doc)
- **Docker**: [docs.docker.com](https://docs.docker.com/)
- **CARLA**: [carla.readthedocs.io](https://carla.readthedocs.io/)
- **YOLO**: [docs.ultralytics.com](https://docs.ultralytics.com/)
