FROM python:3.7-alpine
WORKDIR /parse
COPY ./parse.py /parse
RUN pip install requests
ENTRYPOINT ["python3", "parse.py"]
CMD [""]
