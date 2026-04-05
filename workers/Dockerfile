FROM python:3.12-slim

#install ffmpeg binaries before proceeding
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY workers/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY workers ./workers

CMD ["python","-u","-m","workers.worker"]

