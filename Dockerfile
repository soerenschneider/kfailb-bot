FROM python:3.7-slim

COPY requirements.txt /opt/kfailbot/requirements.txt
WORKDIR /opt/kfailbot
RUN pip install --no-cache-dir -r requirements.txt

COPY kfailbot/* /opt/kfailbot/

RUN useradd toor
USER toor

ENV PYTHONPATH="$PYTHONPATH:/opt/"
CMD ["python3", "cmd.py"]
