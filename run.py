import argparse
import configparser
import email
import imaplib
import logging
import os
import re
import time

from selenium import webdriver

logger = logging.getLogger(__name__)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-c",
        "--config-file",
        dest="config_file",
        default="config.ini",
        help='Absolute or relative path to the configuration file. Must be an ".ini" format',
    )
    args = arg_parser.parse_args()

    config_file = args.config_file
    if not os.path.exists(config_file):
        logger.error(f"Config file {config_file} not exists")
        exit(1)

    logger.info(f"Read config file {config_file}")
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)

    for section in config_parser.sections():
        logger.info(f"Process section {section}")
        host = config_parser.get(section, "host")
        port = config_parser.getint(section, "port", fallback=993)
        user = config_parser.get(section, "user")
        passw = config_parser.get(section, "pass")
        mailbox = config_parser.get(section, "mailbox", fallback="INBOX")
        auto_prune = config_parser.getboolean(section, "auto_prune", fallback=False)
        trash_mailbox = config_parser.get(section, "trash_mailbox")
        chromedriver_path = config_parser.get(section, "chromedriver_path")
        headless = config_parser.get(section, "headless", fallback=False)

        logger.info(f"Connect to IMAP server {host}:{port}")
        imap = imaplib.IMAP4_SSL(host, port)
        imap.login(user, passw)

        logger.info(f"Select mailbox {mailbox} and search for dondino mails")
        imap.select(mailbox)
        _, messages = imap.search(None, '(FROM "info@dondino.de")')
        ids = messages[0].split()
        logger.info(f"Found {len(ids)} dondino mails")

        links = {}
        for id in ids:
            _, data = imap.fetch(id, "(RFC822.TEXT)")
            _, byte_data = data[0]
            email_message = email.message_from_bytes(byte_data)
            for email_part in email_message.walk():
                content_type = email_part.get_content_type()
                if content_type == "text/plain" or content_type == "text/html":
                    content_byte = email_part.get_payload(decode=True)
                    content = content_byte.decode()
                    link_matcher = re.search(r"https://dondino\.de/link/\?\w+", content)
                    if link_matcher:
                        link = link_matcher.group(0)
                        links[id.decode()] = link
                        logger.info(f"Found dondino paid link {link}")
                    else:
                        if auto_prune:
                            _mark_mail_as_deleted(imap, id)

        if links:
            logger.info(f"Found {len(links)} dondino paid links")
            if len(ids) != len(links):
                logger.info(
                    f"There are some dondino mails that may be “Bonus” or “Info” mails and do not contain paid links"
                )

            options = webdriver.ChromeOptions()
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-search-engine-choice-screen")
            if headless:
                options.add_argument("--headless")

            service = None
            if chromedriver_path:
                service = webdriver.ChromeService(executable_path=chromedriver_path)

            driver = webdriver.Chrome(options=options, service=service)
            driver.get("https://dondino.de")

            for id, link in links.items():
                logger.info(f"Open dondino paid link {link}")
                driver.execute_script(f"window.open('{link}');")
                if auto_prune:
                    _mark_mail_as_deleted(imap, id)

            logger.info(
                "Wait 2 minutes before closing the browser to ensure that all dondino pages are fully loaded"
            )
            time.sleep(120)
            driver.quit()

            if auto_prune:
                logger.info("Delete all found dondino mails")
                if _is_gmail_host(imap):
                    imap.select(mailbox=trash_mailbox)
                    imap.store("1:*", "+FLAGS", r"(\Deleted)")
                imap.expunge()
        else:
            logger.info(f"No dondino paid links found")

        logger.info("Disconnect from IMAP server")
        imap.close()
        imap.logout()


def _mark_mail_as_deleted(imap, id):
    if _is_gmail_host(imap):
        imap.store(id, "+X-GM-LABELS", r"(\Trash)")
    else:
        imap.store(id, "+FLAGS", r"(\Deleted)")


def _is_gmail_host(imap):
    return imap.host.endswith("gmail.com")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    main()
