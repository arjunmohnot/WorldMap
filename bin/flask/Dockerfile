FROM python:3.8.2
LABEL maintainer="Sashwat K <sashwat0001@gmail.com>"

ADD . /usr/share/WorldMap/
RUN pip install -r /usr/share/WorldMap/requirements.txt

# Runs app.py
ENV FLASK_APP /usr/share/WorldMap/app.py
ENV FLASK_RUN_HOST 0.0.0.0
CMD ["flask", "run"]