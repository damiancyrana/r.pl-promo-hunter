import os
import json
import smtplib
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from email.header import Header
from urllib.parse import urljoin
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EndingOffers:
    """
    Class for scraping ending offers and sending them via email.
    """

    def __init__(self):
        """
        Initialize EndingOffers class with the default URLs and filenames.
        """
        self.base_directory = "/home/home/r.pl-promo-hunter/"
        self.url_for_ending_offers = "https://r.pl/koncoweczka"
        self.email_template_file = os.path.join(self.base_directory, "email_template.html")
        self.stored_offers_file = os.path.join(self.base_directory, "stored_offers.json")

    def scrape_offers(self):
        """
        Scrape the offers from the URL and return a list of dictionaries with offer details.
        """
        response = requests.get(self.url_for_ending_offers)
        soup = BeautifulSoup(response.text, 'html.parser')
        wrappers = soup.find_all('div', class_='bloczek__wrapper')
        offers = []

        for wrapper in wrappers:
            header_element = wrapper.find('p', class_='bloczek__tytul')
            link_element = wrapper.find('a')
            price_element = wrapper.find('span', class_='bloczek__cena')
            location_element = wrapper.find('span', class_='bloczek__lokalizacja--text')

            # Check if all required elements are present
            if header_element and link_element and price_element and location_element:
                absolute_link = urljoin(self.url_for_ending_offers, link_element['href'])
                offer = {
                    'header': header_element.text.strip(),
                    'location': location_element.text.strip(),
                    'price': price_element.text.strip(),
                    'link': absolute_link,
                }
                offers.append(offer)

        return offers

    def generate_html_message(self, offers):
        """
        Generate HTML message with offer details.

        Args:
            offers (list): List of dictionaries with offer details.

        Returns:
            str: HTML message string.
        """
        with open(self.email_template_file, 'r') as file:
            html_template = file.read()

        offers_html = ""
        for offer in offers:
            offer_html = f"""
            <div class="offer">
                <h2>{offer['header']}</h2>
                <p>Location: {offer['location']}</p>
                <p>Price: {offer['price']} PLN</p>
                <p>Link: <a href="{offer['link']}">View Offer</a></p>
                <hr>
            </div>
            """
            offers_html += offer_html

        return html_template.replace('{{offers}}', offers_html)

    def send_email(self, sender, password, recipient, offers):
        """
        Send an email with offer details.

        Args:
            sender (str): Email sender.
            password (str): Email sender password.
            recipient (str): Email recipient.
            offers (list): List of dictionaries with offer details.
        """
        html_message = self.generate_html_message(offers)

        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = recipient

        current_date = datetime.now().strftime('%Y-%m-%d')
        subject = f"Rainbow Ending Offers - {current_date}"
        message['Subject'] = Header(subject, 'utf-8')

        message.attach(MIMEText(html_message, 'html'))

        # Try to send the email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, message.as_string())
            server.quit()
            logging.info("Email sent successfully!")
        except Exception as e:
            logging.error(f"Error sending email: {e}")

    def get_stored_offers(self):
        """
        Get the previously stored offers.

        Returns:
            list: List of dictionaries with previously stored offers.
        """
        if os.path.exists(self.stored_offers_file):
            with open(self.stored_offers_file, 'r') as file:
                return json.load(file)
        return []

    def store_offers(self, offers):
        """
        Store the current offers to a file.

        Args:
            offers (list): List of dictionaries with current offers.
        """
        with open(self.stored_offers_file, 'w') as file:
            json.dump(offers, file)


def setup_logging():
    logging.basicConfig(
        filename="/home/home/r.pl-promo-hunter/ending_offers.log",
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
    )


def main():
    """
    Main function for scraping and sending offers via email.
    """
    setup_logging()

    # Load email credentials
    with open('/home/home/r.pl-promo-hunter/credentials.json') as json_file:
        credentials = json.load(json_file)

    ending_offers = EndingOffers()

    # Scrape the new offers
    new_offers = ending_offers.scrape_offers()

    # Load the last sent offers
    stored_offers = ending_offers.get_stored_offers()

    # Check if there are new offers and send email if needed
    if new_offers != stored_offers:
        ending_offers.send_email(
            credentials['sender'], credentials['password'], credentials['recipient'], new_offers
        )
        ending_offers.store_offers(new_offers)
    else:
        logging.info("Email not sent due to not found new offers")


if __name__ == "__main__":
    main()
