FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python manage.py migrate && echo \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='testuser').exists() or User.objects.create_superuser('testuser', 'test@test.com', 'testuser123')\" | python manage.py shell && python manage.py runserver 0.0.0.0:8000"]