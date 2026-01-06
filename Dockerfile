version: "3.8"

services:
  chatbot:
    image: fcj-chatbot:latest   # ⬅️ dùng image đã build
    container_name: fcj-chatbot
    ports:
      - "8501:8501"

    env_file:
      - .env

    environment:
      GROQ_API_KEY: ${GROQ_API_KEY}

    volumes:
      - ./vectorstore:/app/vectorstore
      - hf-cache:/tmp/huggingface   # ⬅️ cache model
      - torch-cache:/tmp/torch

    restart: unless-stopped

    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 4G
        reservations:
          memory: 2G

volumes:
  hf-cache:
  torch-cache:
