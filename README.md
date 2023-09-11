# Setup

## Critical prerequisites to install

* run ```pip3 install -r requirements.txt``` or ```pip install -r requirements.txt```

* **Rename the file `.env.example` to `.env`**

* Recommended python version `3.9` +
---

## Run the bot on the desktop

1. Open a terminal or command prompt

2. Navigate to the directory where you installed the ChatGPT Discord bot

3. Run `python3 main.py` or `python main.py` to start the bot
---
## Run the bot with Docker

1. Build the Docker image & Run the Docker container `docker compose up -d`

2. Inspect whether the bot works well `docker logs -t chatgpt-discord-bot`

   ### Stop the bot:

   * `docker ps` to see the list of running services
   * `docker stop <BOT CONTAINER ID>` to stop the running bot

---
## Optional: Disable logging

* Set the value of `LOGGING` in the `.env` to False

---
