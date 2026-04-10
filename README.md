# Simple E-Bidding System

A basic web application built using Flask that allows buyers to create tenders and vendors to submit bids. This project demonstrates core web development concepts like authentication, database handling, and role-based access.

---

## 🚀 Features

* User Registration & Login (Buyer / Vendor)
* Buyers can create and manage tenders
* Vendors can view tenders and submit bids
* Buyers can view bids for each tender
* Simple and clean UI using HTML and CSS
* No JavaScript used (pure server-side rendering)

---

## 🛠️ Tech Stack

* **Frontend:** HTML, CSS
* **Backend:** Python (Flask)
* **Database:** SQLite

---

## 📁 Project Structure

```
project/
│── app.py
│── database.db
│
├── templates/
│   ├── base.html
│   ├── register.html
│   ├── login.html
│   ├── buyer_dashboard.html
│   ├── vendor_dashboard.html
│   ├── create_tender.html
│   ├── submit_bid.html
│   ├── view_bids.html
│
└── static/
    └── css/
```

---

## ⚙️ How to Run

1. Clone the repository:

```
git clone <your-repo-link>
cd project
```

2. Install dependencies:

```
pip install flask
```

3. Run the application:

```
python app.py
```

4. Open in browser:

```
http://127.0.0.1:5000
```

---

## 🗄️ Database

The application uses SQLite with three main tables:

* **users** – stores user details and roles
* **tenders** – stores tender information
* **bids** – stores bids submitted by vendors

---

## 👥 User Roles

### Buyer

* Create tenders
* View bids submitted

### Vendor

* View available tenders
* Submit bids

---

## 🎯 Purpose of the Project

This project was built as a beginner-friendly implementation of an e-bidding system to understand:

* Web development basics using Flask
* Database relationships
* Role-based access control

---

## 🔮 Future Improvements

* Add search and filters for tenders
* Improve UI design
* Add file upload for bid documents
* Implement advanced validation features

---

## 📌 Notes

* This is a basic academic project
* No external APIs or advanced security features are included
* Focus is on simplicity and understanding core concepts

---

## 🙌 Acknowledgment

Built as part of learning full-stack development and exploring real-world system design concepts.
