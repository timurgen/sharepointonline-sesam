FROM python:3-slim
COPY ./service /service
WORKDIR /service
RUN apt-get update && apt-get install git -y

RUN pip install -r requirements.txt
EXPOSE 5000/tcp

RUN  apt-get purge -y --auto-remove git && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["python"]
CMD ["service.py"]