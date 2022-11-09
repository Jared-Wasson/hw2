FROM python:3.9.13
WORKDIR /HW2
COPY comsumer.py comsumer.py
RUN pip install boto3
CMD ["python", "comsumer.py", "dynamo"]