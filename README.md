# 🎌 Anime Kai REST API

<p align="center">
  <img src="https://anikai.to/assets/uploads/37585a3ffa8ec292ee9e2255f3f63b48ceca17ef2a0386.png" alt="Anime Kai Logo" width="200"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Framework-black?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Repo-GitHub-white?style=for-the-badge&logo=github" alt="GitHub">
  <img src="https://img.shields.io/badge/Status-Stable-success?style=for-the-badge" alt="Status">
</p>

---

## 🌟 Overview

**Anime Kai REST API** is a high-performance, developer-first scraping engine designed to unlock the full potential of [AnimeKai](https://anikai.to). By combining advanced HTML parsing with automated token encryption, this API provides a seamless bridge to anime metadata, episode lists, and **direct m3u8 streaming links**.

### 💎 Key Features
- 🎬 **Direct Streaming Resolver:** Automated multi-step decryption to find real `m3u8` video sources.
- 🕒 **Smart Timestamps:** Built-in intro and outro skip points for a premium viewing experience.
- 🏠 **Dynamic Dashboard:** Scrapes homepage banners, latest updates, and trending anime (Now, Day, Week, Month).
- 🧬 **Automated Encryption:** Zero-manual-work integration with `enc-dec.app` for secure token (`_`) parameters.
- 🧼 **Pristine Source Code:** Clean, comment-free, and production-ready Python logic.

---

## 🛠 Architecture & Tech Stack

This project is built using modern Python tools to ensure speed and reliability:
- **Flask:** Lightweight and scalable RESTful API framework.
- **BeautifulSoup4:** Elegant HTML parsing and data extraction.
- **Requests:** Robust HTTP communication with custom header management.
- **Enc-Dec Bridge:** External integration for rolling token security.

---

## 🚀 Installation & Deployment

### 1. Set Up Environment
Ensure you have Python 3.10 or higher installed.
```bash
# Install required packages
pip install flask flask-cors requests beautifulsoup4
```

### 2. Launch the API
```bash
# Clone the repository
git clone https://github.com/walterwhite-69/AnimeKAI-API.git
cd AnimeKAI-API

# Start the server
python app.py
```

---

## 📖 API Documentation

### **Example Discovery Flow**
| Order | Action | Endpoint | Purpose |
| :--- | :--- | :--- | :--- |
| **0** | Search | `GET /api/search?keyword=Naruto` | Find the anime `slug`. |
| **1** | Info | `GET /api/anime/{slug}` | Extract metadata and the key `ani_id`. |
| **2** | Episodes | `GET /api/episodes/{ani_id}` | Retrieve individual episode tokens. |
| **3** | Servers | `GET /api/servers/{ep_token}` | Discover Sub, Dub, and Softsub mirrors. |
| **4** | **Play** | `GET /api/source/{link_id}` | **Final Prize: Direct m3u8 stream!** |

---


---

## 👤 Author & Contribution
Developed and visioned by [**Walter**](https://github.com/walterwhite-69).
Please star the repository for future updates
For contributions, bug reports, or feature requests, visit the official repository:  
🔗 **[GitHub Repository](https://github.com/walterwhite-69/AnimeKAI-API)**

---

<p align="center">Made with ❤️by Walter for the Anime Community. <i>Educational use only.</i></p>
