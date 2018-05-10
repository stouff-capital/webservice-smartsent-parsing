FROM python:3
MAINTAINER Greg Chevalley "gregory.chevalley@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["api.py"]
