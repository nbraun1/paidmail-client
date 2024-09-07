# Paidmail Client

Simple Python script to retrieve [Paidmails (link to German Wikipedia article)](https://de.wikipedia.org/wiki/Paidmail) from the mailbox and click on the paid link in the mail. Optionally, each Paidmail can be deleted automatically.

Tested with:

- Windows 11 - Python 3.12.5 - Chrome Browser 128.0.6613.120 - Gmail
- Debian 12 (Bookworm ARM64) - Python 3.11.2 - Chrome Driver 128.0.6613.119 - Gmail

## Supported Paidmailer

If you know of a reputable Paidmailer that I should add to this script, please let me know! :)

- [dondino.de](https://dondino.de)

## Prerequisites

- Python
- Pip
- Optional, but recommended: Python [virtual environments](https://docs.python.org/3/library/venv.html)
- Chrome Browser or Chrome Driver

## Run the Script

1. Clone this repository
2. Navigate to the root directory of the project
3. Copy [standard.config.ini](./examples/standard.config.ini) to `config.ini` and adapt the configuration to your requirements (see the section [configuration](#configuration))
4. Run `pip install -r requirements.txt`
5. Run `python run.py`

## Configuration

Examples of configurations can be found in the ini files in [this](./examples/) folder.

| **Property**      | **Description**                                                                                                                                                                         | **Default** |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
| host              | Imap server hostname                                                                                                                                                                    |             |
| port              | Imap server port                                                                                                                                                                        | 993         |
| user              | Your username                                                                                                                                                                           |             |
| pass              | Your password                                                                                                                                                                           |             |
| mailbox           | Mailbox from which the Paidmails are read                                                                                                                                               | INBOX       |
| auto_prune        | Whether the Paidmails found should be deleted automatically                                                                                                                             | false       |
| trash_mailbox     | Mailbox in which the deleted mails are saved and should be removed if `auto_prune` is `true`. In Gmail, for example, this is “[Gmail]/Trash”                                            |             |
| chromedriver_path | Path to the Chrome driver. Not required if you are using the Chrome browser                                                                                                             |             |
| headless          | Links in found Paidmails are opened in a browser with Selenium. If `headless` is `true`, the browser will **not** open in a GUI. Useful for devices that are not connected to a monitor | false       |
