# 🎬 MovieBox Blogger Sync Bot

Automated GitHub Action bot that scrapes latest trending movies, builds **1-Click Deep Links for VLC & MX Player**, and automatically publishes them to your **Blogger** website every 6 hours!

---

## 📱 Kaise Kaam Karta Hai?

1. **GitHub Action (Cloud):** Har 6 ghante me automatically run hota hai. Latest movies aur direct stream links scrape karta hai.
2. **Auto Post to Blogger:** Blogger ke secret email ke zariye automatically beautiful post publish kar deta hai.
3. **Mobile Playback:** Jab aap phone ke browser me apna Blogger blog kholkar **"Play in VLC"** ya **"Play in MX Player"** par tap karoge, toh phone bina kisi popup/ads ke direct **VLC** me movie play kar dega!

---

## 🛠️ Step-by-Step Setup Guide

### Step 1: Blogger me Secret Email Setup Karein

1. Apne **Blogger Dashboard** me jayein (`blogger.com`).
2. Left side menu se **Settings** par click karein.
3. Scroll karke **Email** section me jayein:
   - **"Post using email"** option par click karein.
   - Choose karein: **"Publish email immediately"**.
   - Ek secret word daalein (Jaise: `mysecret123`).
   - Ab aapka secret email ban jayega: `username.mysecret123@blogger.com`
4. Is email address ko copy kar lein.

---

### Step 2: Gmail App Password Generate Karein (SMTP ke liye)

GitHub Actions se Blogger ko email bhejne ke liye Gmail ka ek App Password chahiye:
1. Apne Google Account me jayein: [Google Account Security](https://myaccount.google.com/security)
2. **2-Step Verification** ON karein (agar pehle se ON nahi hai).
3. Search bar me type karein **"App Passwords"** (ya 2-Step Verification ke andar neeche jayein).
4. App name likhein: `BloggerBot` aur **Create** karein.
5. 16-digit ka password milega (jaise `abcd efgh ijkl mnop`). Isko copy kar lein.

---

### Step 3: GitHub Repository Create & Push Karein

Apne computer terminal (PowerShell / Command Prompt) me is folder ke andar ye commands run karein:

```bash
cd "c:\Users\biswa\Downloads\mobile hot\moviebox-blogger-sync"
git init
git add .
git commit -m "feat: initial commit for moviebox blogger sync bot"
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git
git push -u origin main
```

---

### Step 4: GitHub Secrets Add Karein

1. Apne GitHub Repo me jayein -> **Settings** tab par click karein.
2. Left menu me **Secrets and variables** -> **Actions** par click karein.
3. **New repository secret** par click karke ye 3 secrets add karein:

| Secret Name | Value |
| :--- | :--- |
| `BLOGGER_SECRET_EMAIL` | Step 1 wala Blogger email (`username.secret@blogger.com`) |
| `SMTP_USER` | Aapka Gmail address (`yourname@gmail.com`) |
| `SMTP_PASS` | Step 2 wala 16-letter Gmail App Password (`abcdefghijklmnop`) |

---

### Step 5: Test Run Karein (1-Click)

1. Apne GitHub Repo ke **Actions** tab par jayein.
2. Left side me **"Auto Sync Movies to Blogger"** workflow select karein.
3. Right side me **"Run workflow"** button dabayein!
4. 1 minute me workflow complete ho jayega aur aapke Blogger par naye movie posts publish ho jayenge!

---

## 🍿 Mobile se Kaise Play Karein?

1. Apne phone me Blogger blog open karein.
2. Kisi bhi movie post par jayein.
3. **[▶ Open in VLC Player]** button par tap karein.
4. Phone me **VLC for Android** open ho jayega aur video bina kisi buffer ke chalne lagegi!

