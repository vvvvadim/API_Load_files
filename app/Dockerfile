FROM python:3.12
ENV TZ=Europe/Moscow
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .