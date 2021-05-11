FROM python:3.8
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "get-from-odsluchane-remote-adsl.py"]