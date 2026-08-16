FROM mcr.microsoft.com/playwright/python:v1.61.0-resolute

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["pytest", "--browser", "chromium", "-n", "2"]
