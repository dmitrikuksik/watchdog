# Linux Service Watchdog

Nordcloud Recruitment Assignment.

# Requirements
* Linux
* Python > 3.6.9
* virtualenv

# Installation

1. Create virtual environment for project:
```bash
virtualenv -p python3 venv
```

2. Activate created virtual environment:
```bash
source venv/bin/activate
```

3. Install Python requirements:
```bash
pip install -r requirements.txt
```

4. Export all required environment variables:
```bash
export AWS_REGION=<your-region>
export AWS_ACCOUNT_ID=<your-account-id>
export AWS_ACCESS_KEY_ID=<your-access-key-id>
export AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
export AWS_WATCHDOG_TABLE=<your-watchdog-table-name>
export AWS_WATCHDOG_SNS_TOPIC=<your-watchdog-sns-topic>
```

5. Run Watchdog:
```bash
python -m watchdog -i <watchdog-settings-id>
```

# Run as a Linux service

1. Add required permissions:
```bash
chmod +x install.bash 
```

2. Install service (run sudo -E if needed):
```bash
./install <watchdog-settings-id>
```

3. Run service:
```bash
systemctl start watchdog.service
```
