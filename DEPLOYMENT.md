# CI/CD Pipeline Documentation

## Overview
Automated CI/CD pipeline using GitHub Actions for the FCAJ Chatbot project.

## Pipeline Stages

### 1. Continuous Integration (CI)

#### Lint
- Runs `flake8` for code quality checks
- Runs `black` for code formatting validation
- Triggers on: Push/PR to main or develop branches

#### Test
- Executes pytest test suite
- Generates code coverage report
- Requires: Lint stage to pass

#### Build
- Builds Docker image
- Tags with commit SHA
- Uploads artifact for deployment
- Requires: Lint and Test stages to pass

### 2. Continuous Deployment (CD)

#### Deploy to Development
- Triggers: Push to `develop` branch only
- Deploys to development environment
- Uses Docker container registry (GHCR)
- SSH deployment to development server

## Required Secrets

Configure these in GitHub Settings → Secrets and variables → Actions:

```
DEV_HOST          # Development server IP/hostname
DEV_USER          # SSH username
DEV_SSH_KEY       # SSH private key
GROQ_API_KEY      # Groq API key for the application
```

## Server Setup (Development)

1. Install Docker and Docker Compose on server
2. Create deployment directory:
```bash
mkdir -p /opt/fcaj-chatbot
cd /opt/fcaj-chatbot
```

3. Copy `docker-compose.dev.yml` to server as `docker-compose.yml`

4. Create `.env` file:
```bash
GROQ_API_KEY=your_key_here
GITHUB_REPOSITORY=username/repo
```

5. Login to GitHub Container Registry:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

## Manual Deployment

```bash
# Pull latest image
docker-compose pull

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart
docker-compose restart
```

## Workflow Triggers

- **Push to main**: Runs CI only
- **Push to develop**: Runs CI + Deploy to Development
- **Pull Request**: Runs CI only

## Monitoring

Check deployment status:
- GitHub Actions tab for pipeline status
- Development URL: http://dev.fcaj-chatbot.com
- Server logs: `docker-compose logs -f`
