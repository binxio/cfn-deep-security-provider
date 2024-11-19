FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.9

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY --chmod=0555 ./entrypoint.sh /entrypoint.sh

COPY src/ ./

RUN find . -type d -print0 | xargs -0 chmod ugo+rx && \
    find . -type f -print0 | xargs -0 chmod ugo+r


ENV HANDLER=provider

ENTRYPOINT ["/entrypoint.sh"]
