# 📢 ABES Digital Notice Board

A modern web-based Notice Board Management System built using **Flask**, **SQLite**, **Bootstrap 5**, and **Chart.js**. The application enables administrators to create, manage, and organize notices efficiently while providing students with an intuitive interface to browse announcements.

> 🎓 CS50x Final Project

---

## 📸 Preview

> *(Add screenshots here after uploading them.)*

| Login | Dashboard |
|-------|-----------|
| ![](/static/screenshots/login.png) | ![](/static/screenshots/dashboard.png) |

| Home | Notice Details |
|------|----------------|
| ![](/static/screenshots/home.png) | ![](/static/screenshots/notice.png) |

---

# ✨ Features

## 🔐 Authentication

- Secure Login
- User Registration
- Password Hashing
- Session Management

---

## 📢 Notice Management

- Create Notice
- Edit Notice
- Delete Notice
- Pin / Unpin Notices
- Notice Categories
- Department Selection
- Search Notices
- Filter by Category
- Pagination

---

## 📂 File Uploads

Supports:

- Images
- PDF Documents

Uploaded files can be viewed directly from the application.

---

## 📊 Dashboard

Interactive dashboard including:

- Total Notices
- Pinned Notices
- Categories
- Departments
- Recent Notices
- Analytics Charts
- Quick Statistics

Powered by **Chart.js**.

---

## 🎨 UI Features

- Responsive Design
- Bootstrap 5
- Dark Mode
- Toast Notifications
- Custom Delete Confirmation Modal
- Hover Animations
- Count-Up Statistics
- Custom 404 & 500 Error Pages

---

# 🛠 Tech Stack

### Backend

- Python
- Flask
- SQLite

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Jinja2

### Libraries

- Chart.js
- Werkzeug

---

# 📂 Project Structure

```
ABES-Digital-Notice-Board/

│
├── static/
│   ├── css/
│   ├── js/
│   ├── uploads/
│   └── images/
│   └── screenshots/
│
├── templates/
│   ├── layout.html
│   ├── login.html
│   ├── register.html
│   ├── index.html
│   ├── dashboard.html
│   ├── add_notice.html
│   ├── edit_notice.html
│   ├── notice.html
│   ├── view_notice.html
│   ├── 404.html
│   └── 500.html
│
├── app.py
├── config.py
├── helpers.py
├── notices.db
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ABES-Digital-Notice-Board.git
```

Move into the project

```bash
cd ABES-Digital-Notice-Board
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
flask run
```

Open your browser

```
http://127.0.0.1:5000
```

---

# 📖 How to Use

1. Register a new account.
2. Log in securely.
3. Add new notices.
4. Upload PDFs or images.
5. Pin important notices.
6. Search or filter announcements.
7. Monitor analytics from the dashboard.
8. Edit or delete notices whenever required.

---

# 🌟 Future Enhancements

- Email Notifications
- Admin Roles
- Student Portal
- QR Code Sharing
- Notice Expiry Dates
- Mobile Application
- REST API
- Cloud Storage Integration

---

# 📚 What I Learned

During this project, I strengthened my understanding of:

- Flask Routing
- Authentication
- CRUD Operations
- SQLite Databases
- Jinja Templates
- Bootstrap 5
- JavaScript
- Chart.js
- Responsive Web Design
- UI/UX Principles

---

# 👨‍💻 Author

**Mohammad Fazal**

B.Tech Computer Science Student

ABES Engineering College

---

# 🙏 Acknowledgements

- Harvard CS50
- Flask Documentation
- Bootstrap Documentation
- Chart.js Documentation

---

## ⭐ If you like this project, consider giving it a star!