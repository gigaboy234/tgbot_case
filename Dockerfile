FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create volume mount point for persistent data
VOLUME ["/app/bot.sqlite3"]

# Set environment variables (can be overridden at runtime)
ENV BOT_TOKEN=""
ENV ADMIN_CHAT_ID=""
ENV LOG_LEVEL="INFO"

# Run the bot
CMD ["python", "main.py"]
