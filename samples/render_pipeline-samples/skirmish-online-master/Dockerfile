FROM python

RUN mkdir -p /opt/skirmish
WORKDIR /opt/skirmish

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install wget lsb-release
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update
RUN apt-get -y install postgresql

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN rm requirements.txt

RUN useradd skirmish
RUN chown -R skirmish:skirmish /opt/skirmish
RUN chmod -R 700 /opt/skirmish

COPY server /opt/skirmish/server
COPY protocol /opt/skirmish/protocol

USER skirmish

CMD ["python", "-mserver"]
