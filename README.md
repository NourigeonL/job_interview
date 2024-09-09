# Gena Backend Engineer Programming Test

## How to run the code
### Step 1: clone the repository 
    git clone https://github.com/NourigeonL/job_interview.git
### Step 2: Run docker compose
- change the env variables in .docker.env file
- run `docker-compose up -d`
### Step 3 (only first run): migrate the database
1. create a temporary python virtual environment
2. create a .env file and set the necessary environmnent variables
2. run 
    ```
    pip install alembic sqlmodel asyncpg pydantic_settings
    alembic upgrade head
    ```
### Step 4: ?????
### Step 5: profit