## Docker Quick Start

- Create .env using .env.example as reference

```bash
cp .env.example .env
```

- Configure required environment values and run docker-compose

```bash
docker-compose up -d
```

## Installing from Source

### Prerequisites

- python3
- virtualenv
- docker
- docker-compose


### Installing

A step by step series of examples that tell you how to get a development env running

Clone the Project 

```bash
git clone https://github.com/Rishang/aws-oidc-broker.git
```

Initialzing virtualenv

```bash
cd aws-oidc-broker
python -m venv venv
source ./venv/bin/activate
```

Installing Dependencies

```bash
pip install -r requirements.txt
```

Configure .env file or perform export of those variables

```bash
cp .env.example .env
```

Configure environment variables as required.