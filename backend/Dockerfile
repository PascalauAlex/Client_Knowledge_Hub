FROM dhi.io/python:3.14-debian13-dev AS builder
LABEL authors="Pascalau Alexandru Marian"


WORKDIR /app

RUN python3 -m venv /venv

ENV PATH="/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install libmagic1 -y


RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt


COPY . .

EXPOSE 8000

CMD ["uvicorn","main:app","--reload","--host=0.0.0.0","--port=8000"]

FROM dhi.io/python:3.14-debian13 AS production

WORKDIR /app

# libmagic: biblioteca (fișierul real + symlink-ul)
COPY --from=builder /usr/lib/x86_64-linux-gnu/libmagic.so.1 /usr/lib/x86_64-linux-gnu/libmagic.so.1.0.0 /usr/lib/x86_64-linux-gnu/

# baza de date: fișierul real + symlink-ul prin care e căutat
COPY --from=builder /usr/lib/file/magic.mgc /usr/lib/file/magic.mgc
COPY --from=builder /usr/share/misc/magic.mgc /usr/share/misc/magic.mgc

# configurare locală
COPY --from=builder /etc/magic /etc/magic.mime /etc/
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

COPY . .


EXPOSE 8000

USER nonroot

CMD ["uvicorn","main:app","--host=0.0.0.0","--port=8000"]








