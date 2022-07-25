FROM python:3.10-alpine

RUN adduser -D bot
USER bot
WORKDIR /home/bot

ENV PATH="${PATH}:/home/bot/.local/bin"

RUN /usr/local/bin/python -m pip install --user --upgrade pip

COPY --chown=bot:bot requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY --chown=bot:bot main.py main.py

CMD [ "python3", "main.py" ]
