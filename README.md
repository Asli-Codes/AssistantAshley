# 🎙️ Ashley – Turkish Voice Assistant

Ashley is an AI-powered personal assistant that understands **Turkish voice commands**
and responds appropriately using speech recognition and natural language processing techniques.
The project combines **Speech-to-Text (STT)**, **NLP**, and a simple **user interface**
to create a practical and interactive voice assistant application.

---

## 🚀 Project Purpose

The main goal of this project is to develop a smart assistant that can:
- understand **spoken Turkish commands**,
- analyze the **user’s intent**,
- execute the related action,
- and return the result both **visually** and **audibly**.

---

## 🧠 Features

- 🎙️ Turkish Speech Recognition (Speech-to-Text)
- 🧠 Intent detection using rule-based NLP
- 📝 Note creation and note listing
- ⏰ Reminder management
- ➗ Basic mathematical calculations
- 🔊 Text-to-Speech responses
- 🖥️ Streamlit-based user interface
- 📦 Modular and extensible project structure

---

## 🧩 Technologies Used

| Area | Technology |
|----|----|
| Programming Language | Python |
| Speech-to-Text | Vosk (Turkish model) |
| Natural Language Processing | Rule-based NLP |
| Text-to-Speech | pyttsx3 |
| User Interface | Streamlit |
| Data Storage | JSON |
| Supporting Libraries | NumPy, SciPy, SoundDevice |

> ℹ️ Note: The Whisper library was not used due to dependency incompatibilities
with Python 3.13. Instead, Vosk was preferred as a stable, offline, and Windows-friendly
speech recognition solution.

---

## 📁 Project Structure

```text
Ashley/
├─ app.py
├─ README.md
├─ requirements.txt
├─ data/
│  ├─ commands.json
│  ├─ notes.json
│  └─ reminders.json
├─ models/
│  └─ vosk-model-small-tr-0.3/
├─ modules/
│  ├─ speech_to_text.py
│  ├─ text_to_speech.py
│  └─ intent_handler.py
