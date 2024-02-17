FROM python:3.10
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


#FROM ubuntu
#
#MAINTAINER TEPLAKOKKA DEV <order@teplakokka.ru>
#
#RUN apt-get update && apt-get install -y cowsay && ln -s /usr/games/cowsay /usr/bin/cowsay
#
#ENTRYPOINT ["cowsay"]
#
#
