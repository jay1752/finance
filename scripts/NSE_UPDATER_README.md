# NSE Data Updater Service

Automated daily updates of NSE-specific data (FII/DII and delivery percentage).

## What it does

1. **FII/DII Data**: Fetches daily institutional investment data from NSE
   - Foreign Institutional Investors (FII) activity
   - Domestic Institutional Investors (DII) activity
   - Stores in `fii_dii_data` table

2. **Delivery Percentage**: Fetches delivery data for all active stocks
   - Shows genuine buying vs speculation
   - Stores in `delivery_data` table

## Usage

### Run Once (Manual)

```bash
# Activate virtual environment
source venv/bin/activate

# Run update once
python scripts/nse_data_updater.py --once
```

### Run as Scheduled Service

```bash
# Run with default schedule (daily at 5:30 PM)
python scripts/nse_data_updater.py

# Run with custom schedule (e.g., 6:00 PM)
python scripts/nse_data_updater.py --hour 18 --minute 0
```

The service will run continuously and execute updates daily at the specified time.

## Scheduling Options

### Option 1: Using the Built-in Scheduler (Recommended)

The script includes APScheduler for automatic scheduling:

```bash
# Run in background using nohup
nohup python scripts/nse_data_updater.py > logs/nse_updater_service.log 2>&1 &

# Or use screen/tmux for interactive monitoring
screen -S nse-updater
python scripts/nse_data_updater.py
# Detach with Ctrl+A, D
```

### Option 2: Using Cron (Linux/macOS)

Add to crontab for daily execution:

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 5:30 PM)
30 17 * * * cd /path/to/finance && source venv/bin/activate && python scripts/nse_data_updater.py --once >> logs/nse_cron.log 2>&1
```

### Option 3: Using systemd (Linux)

Create a systemd service file:

```bash
# /etc/systemd/system/nse-updater.service
[Unit]
Description=NSE Data Updater Service
After=network.target postgresql.service

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/finance
Environment="PATH=/path/to/finance/venv/bin"
ExecStart=/path/to/finance/venv/bin/python scripts/nse_data_updater.py
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl enable nse-updater
sudo systemctl start nse-updater
sudo systemctl status nse-updater
```

### Option 4: Using launchd (macOS)

Create a plist file:

```bash
# ~/Library/LaunchAgents/com.finance.nse-updater.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.finance.nse-updater</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/finance/venv/bin/python</string>
        <string>/path/to/finance/scripts/nse_data_updater.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/finance</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>17</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/path/to/finance/logs/nse_updater.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/finance/logs/nse_updater_error.log</string>
</dict>
</plist>
```

Then load:

```bash
launchctl load ~/Library/LaunchAgents/com.finance.nse-updater.plist
launchctl start com.finance.nse-updater
```

## Configuration

### Update Schedule

Default: Daily at 17:30 (5:30 PM IST) - after market closes

You can change this:
- Using command-line args: `--hour 18 --minute 0`
- Or modify the cron/systemd/launchd configuration

### Logging

Logs are written to:
- `logs/nse_updater.log` - Main log file
- Console output (when running interactively)

Log level can be adjusted in the script (currently INFO).

## Database Requirements

The script requires:
1. PostgreSQL database running
2. Tables created:
   - `fii_dii_data`
   - `delivery_data`
   - `stocks` (with active stocks)

Run database setup first:
```bash
python scripts/setup_db.py
python scripts/seed_nifty50.py
```

## Monitoring

### Check Logs

```bash
# Tail live log
tail -f logs/nse_updater.log

# View recent errors
grep ERROR logs/nse_updater.log

# Check last update
grep "NSE DAILY DATA UPDATE - COMPLETED" logs/nse_updater.log | tail -1
```

### Check Database

```sql
-- Check latest FII/DII data
SELECT * FROM fii_dii_data ORDER BY date DESC LIMIT 5;

-- Check delivery data count
SELECT date, COUNT(*) as stock_count
FROM delivery_data
GROUP BY date
ORDER BY date DESC
LIMIT 5;

-- Check recent delivery for specific stock
SELECT s.symbol, d.*
FROM delivery_data d
JOIN stocks s ON d.stock_id = s.id
WHERE s.symbol = 'RELIANCE'
ORDER BY d.date DESC
LIMIT 5;
```

## Troubleshooting

### NSE Returns 403 Errors

- NSE has anti-bot measures
- Try running during off-market hours (after 6 PM)
- Increase delays between requests
- Check if NSE website structure has changed

### No Data Received

- Market might be closed (weekends/holidays)
- NSE API endpoints might have changed
- Check network connectivity
- Review logs for specific errors

### Database Connection Errors

- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database tables exist

## Best Practices

1. **Run during off-market hours**: 5:30 PM - 9 PM IST
2. **Monitor logs regularly**: Check for errors and failures
3. **Database backups**: Regular backups of FII/DII and delivery data
4. **Respect NSE servers**: Don't run too frequently (once daily is sufficient)
5. **Error handling**: Script continues on individual stock failures

## Environment Variables

Required in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/market_analysis
NSE_SCRAPING_ENABLED=true
```

## Manual Testing

Test individual functions:

```python
# Test FII/DII update
python -c "from scripts.nse_data_updater import update_fii_dii_data; update_fii_dii_data()"

# Test delivery data update
python -c "from scripts.nse_data_updater import update_delivery_data; update_delivery_data()"
```

## Support

For issues:
1. Check logs: `logs/nse_updater.log`
2. Verify NSE website is accessible
3. Test NSE scraper directly: `python src/data/providers/free/nse_scraper.py`
4. Check database connectivity: `python test_setup.py`
