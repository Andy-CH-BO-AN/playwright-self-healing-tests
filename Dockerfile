FROM mcr.microsoft.com/playwright/python:v1.61.0-resolute

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["pytest"]
