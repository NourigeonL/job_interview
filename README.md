# Gena Backend Engineer Programming Test

## How to run the code
### Step 1: clone the repository 
    git clone https://github.com/NourigeonL/job_interview.git
### Step 2: Run docker compose
- change the env variables in .docker.env file
- run `docker-compose up -d`
### Step 3 (only first run): migrate the database
1. In case you change the database configuration, update the `sqlalchemy.url=` variable in `alembic.ini` file (by default `sqlalchemy.url = postgresql+asyncpg://admin:admin@localhost/db`)
2. create a temporary python virtual environment
3. run 
    ```
    pip install alembic sqlmodel asyncpg
    alembic upgrade head
    ```
### Step 4: ?????
### Step 5: profit