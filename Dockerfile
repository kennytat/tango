FROM python:3.10-bullseye


WORKDIR /app

COPY . .

RUN pip install -e . && rm -rf /root/.cache/pip

EXPOSE 7899

ENTRYPOINT [ "python3", "main.py" ]