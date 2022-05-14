FROM fedora:35

COPY querygd /app
COPY requirements.txt /app

WORKDIR /app

RUN chmod +x dbsetup/dbsetup.py

RUN dnf install python3-pip -y
RUN pip3 install -r requirements.txt

ENV PYTHONPATH="/app:/app/dbsetup:$PYTHONPATH"
