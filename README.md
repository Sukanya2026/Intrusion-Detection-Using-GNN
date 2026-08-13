# Dynamic Graph Based Network Intrusion Detection

Small Django project that demonstrates network intrusion detection using Graph Neural Networks (GNNs). The repository contains the Django app, templates, and minimal static assets required to run a local demo.

Quick start (development):

1. Create a virtual environment and activate it:
```bash
py -3 -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
```
2. Install dependencies:
```bash
py -3 -m pip install -r requirements.txt
```
3. Run migrations and start the dev server:
```bash
py -3 manage.py migrate
py -3 manage.py runserver
```
4. Open `http://127.0.0.1:8000/` in your browser.

Notes:
- Do NOT commit `db.sqlite3`, model binary files (`*.pth`) or `media/`.
- Use `Dynamic_Graph_Based_Network_Intrusion/settings_example.py` as a guide for environment-specific settings. Do not commit secrets.
