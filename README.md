# Rainbow Ending Offers Scraper

This script scrapes ending offers from Rainbow website and sends them via email, if there are any new offers. It is designed to run on a Raspberry Pi 4 and can be scheduled to execute at regular intervals using a cron job.

## Getting Started

### Prerequisites

- A Raspberry Pi with Raspbian OS installed
- Python 3.7 or higher

### Dependencies

This script depends on Python beautifulsoup4 librarie. Install them using pip:

```sh
pip install requests beautifulsoup4
```

### Generating App Password for Gmail
As per Google's security guidelines, it's recommended to use App Passwords for scripts and applications that require access to your Google account. Follow these steps to generate an App Password:

1. Visit your Google Account.
2. Select Security,
3. Under "Signing in to Google," select App Passwords (You may need to sign in again),
4. At the bottom, choose the Select app dropdown and choose the app you’re using,
5. Choose the Select device dropdown and choose the device you’re using,
6. Select Generate,
7. Follow the instructions to enter the App Password. The App Password is the 16-character code in the yellow bar on your device,
8. Select Done.

Store the generated App Password in a credentials.json file structured as follows:

```json
{
    "sender": "your-email@gmail.com",
    "password": "your-app-password",
    "recipient": "recipient-email@gmail.com"
}
```

### Running the Script
To execute the script on your Raspberry Pi, navigate to the directory where the script is located, and run the following command:

```sh
python r.py
```

### Scheduling the Script using CRON
To schedule the script to run automatically at regular intervals (e.g., every 30 minutes), you can set up a cron job

1. Open crontab with the following command:

```sh
crontab -e
```

2. Add a new cron job by adding the following line at the end of the file (make sure to replace /path/to/script with the actual path to the script):

```sh
*/30 * * * * /usr/bin/python3 /path/to/script/r.py
```

This line schedules the script to run every 30 minutes. Save the file and exit the editor.

The script is now set up to scrape ending offers and notify you via email if there are any new ones!!!

### License
This project is open source and available under the MIT License
