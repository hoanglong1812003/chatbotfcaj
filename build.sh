#!/bin/bash

echo "Building optimized image..."
docker build -f Dockerfile.optimized -t fcj-chatbot:optimized .

echo -e "\nImage size:"
docker images fcj-chatbot:optimized --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo -e "\nTo run:"
echo "docker run -p 8501:8501 --env-file .env fcj-chatbot:optimized"