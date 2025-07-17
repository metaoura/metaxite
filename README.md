# BanCheck API Discord Bot

A Discord bot that checks if a user is banned via the BanCheck API.

## Features

- Prefix command: `!bancheck <UID>`
- Slash command: `/bancheck <UID>`
- Displays **`is_banned`**, **`period_month`**, **`daily_limit`**, **`usage_count today`**, etc.
- Shows **API response time** in **seconds**.
- Button to join support server (Link Button).
- Dockerfile for containerization (optional).

## Installation

1. Clone this repository or copy the files.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
