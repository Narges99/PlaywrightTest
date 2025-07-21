FROM mcr.microsoft.com/playwright/python:v1.53.0-jammy

WORKDIR /app

RUN apt-get update && apt-get install -y cron

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

COPY cronjob /etc/cron.d/playwright-cron

RUN chmod 0644 /etc/cron.d/playwright-cron

RUN touch /var/log/cron.log

CMD ["cron", "-f"]