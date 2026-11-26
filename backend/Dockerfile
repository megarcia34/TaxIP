FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Argentina/Buenos_Aires

WORKDIR /app

# Instalamos tzdata explícitamente junto con las dependencias del sistema
RUN apt-get update && apt-get install -y \
    tzdata \
    libpq-dev \
    gcc \
    g++ \
    libgeos-dev \
    libproj-dev \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "run.py"]