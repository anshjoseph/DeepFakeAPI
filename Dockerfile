FROM python:3-alpine AS builder
 
WORKDIR /app
 
RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
 
COPY build.sh .
RUN ./build.sh
 
# Stage 2
FROM python:3-alpine AS runner
 
WORKDIR /app
 
COPY --from=builder /app/venv venv
COPY . ./app/
 
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
 
EXPOSE 8000
 
CMD [ "python3", "app.py"]