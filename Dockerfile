FROM python:3-alpine AS builder
 
WORKDIR /app
 
RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
 
COPY build.sh /app/
RUN  chmod +x ./build.sh
RUN  ./build.sh
 
COPY --from=builder /app/venv venv
COPY . /app/
 
 
EXPOSE 8000
 
CMD [ "python3", "/app/app.py"]