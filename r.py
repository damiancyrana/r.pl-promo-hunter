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


class RainbowOffers:
    def __init__(self, base_directory, url, stored_offers_filename):
        self.base_directory = base_directory
        self.url = url
        self.email_template_file = os.path.join(self.base_directory, "email_template.html")
        self.stored_offers_file = os.path.join(self.base_directory, stored_offers_filename)

    def scrape_offers(self, wrapper_selector, header_selector, price_selector, location_selector):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        wrappers = soup.select(wrapper_selector)
        offers = []

        for wrapper in wrappers:
            header_element = wrapper.select_one(header_selector)
            link_element = wrapper.find('a')
            price_element = wrapper.select_one(price_selector)
            location_element = wrapper.select_one(location_selector)

            if header_element and link_element and price_element and location_element:
                absolute_link = urljoin(self.url, link_element['href'])
                offer = {
                    'header': header_element.text.strip(),
                    'location': location_element.text.strip(),
                    'price': price_element.text.strip(),
                    'link': absolute_link,
                }
                offers.append(offer)

        return offers

    def generate_html_message(self, offers, new_offer_headers, price_changed_headers, stored_offers):
        with open(self.email_template_file, 'r') as file:
            html_template = file.read()

        offers_html = ""
        for offer in offers:
            header_color = '#333'
            price_color = '#333'
            old_price = ''
            price_difference_html = ''
            if offer['header'] in new_offer_headers:
                header_color = 'red'
            if offer['header'] in price_changed_headers:
                old_price = stored_offers[offer['header']]['price']
                cleaned_price = offer['price'].replace(" ", "")
                cleaned_old_price = old_price.replace(" ", "")
                try:
                    if float(cleaned_price) < float(cleaned_old_price):
                        price_color = 'green'
                        price_difference_html = f""" <span style="color: {price_color};">(było {old_price} PLN)</span>"""
                    elif float(cleaned_price) > float(cleaned_old_price):
                        price_color = 'red'
                        price_difference_html = f""" <span style="color: {price_color};">(było {old_price} PLN)</span>"""
                except ValueError:
                    logging.error(f"Nie można przekonwertować ceny na float: {cleaned_price} lub {cleaned_old_price}")

            offer_html = f"""
            <div class="offer">
                <h2 style="color: {header_color};">{offer['header']}</h2>
                <p>Lokalizacja: {offer['location']}</p>
                <p>Cena: {offer['price']} PLN{price_difference_html}</p>
                <p>Link: <a href="{offer['link']}">Zobacz ofertę</a></p>
                <hr>
            </div>
            """
            offers_html += offer_html

        return html_template.replace('{{offers}}', offers_html)


    def send_email(self, sender, password, recipient, offers, new_offer_headers, price_changed_headers, stored_offers):
        html_message = self.generate_html_message(offers, new_offer_headers, price_changed_headers, stored_offers)

        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = recipient

        current_date = datetime.now().strftime('%Y-%m-%d')
        subject = f"Rainbow Offers - {current_date}"
        message['Subject'] = Header(subject, 'utf-8')

        message.attach(MIMEText(html_message, 'html'))

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
        if os.path.exists(self.stored_offers_file):
            with open(self.stored_offers_file, 'r') as file:
                return json.load(file)
        return {}

    def store_offers(self, offers):
        offers_dict = {offer['header']: offer for offer in offers}
        with open(self.stored_offers_file, 'w') as file:
            json.dump(offers_dict, file)


class EndingOffers(RainbowOffers):
    def __init__(self):
        super().__init__("/home/home/r.pl-promo-hunter/", "https://r.pl/koncoweczka", "stored_ending_offers.json")

    def scrape_offers(self):
        return super().scrape_offers(
            'div.bloczek__wrapper',
            'p.bloczek__tytul',
            'span.bloczek__cena',
            'span.bloczek__lokalizacja--text'
        )


class HappyHours(RainbowOffers):
    def __init__(self):
        super().__init__("/home/home/r.pl-promo-hunter/", "https://r.pl/happy-hours", "stored_happy_hours_offers.json")

    def should_send_email(self):
        now = datetime.now()
        return now.weekday() < 5 and 13 <= now.hour < 15


    def scrape_offers(self):
        if self.should_send_email():
            return super().scrape_offers(
                'div.bloczki-lp__content > div.bloczek__wrapper',
                'p.bloczek__tytul.h4',
                'span.bloczek__cena.h1',
                'span.bloczek__lokalizacja--text'
            )
        else:
            return []

    def generate_html_message(self, offers, new_offer_headers, price_changed_headers, stored_offers):
        html_message = super().generate_html_message(offers, new_offer_headers, price_changed_headers, stored_offers)
        return html_message.replace("New Rainbow Ending Offers", "New Rainbow Happy Hours Offers")

    def send_email(self, sender, password, recipient, offers, new_offer_headers, price_changed_headers, stored_offers):
        html_message = self.generate_html_message(offers, new_offer_headers, price_changed_headers, stored_offers)

        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = recipient

        current_date = datetime.now().strftime('%Y-%m-%d')
        subject = f"Rainbow Happy Hours Offers - {current_date}"
        message['Subject'] = Header(subject, 'utf-8')

        message.attach(MIMEText(html_message, 'html'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, message.as_string())
            server.quit()
            logging.info("Email sent successfully!")
        except Exception as e:
            logging.error(f"Error sending email: {e}")


def setup_logging():
    logging.basicConfig(
        filename="ending_offers.log",
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
    )


def main():
    setup_logging()

    with open('credentials.json') as json_file:
        credentials = json.load(json_file)

    ending_offers = EndingOffers()
    new_offers = ending_offers.scrape_offers()

    # Check if stored_offers_file exists, if not, consider it the first run
    first_run = not os.path.exists(ending_offers.stored_offers_file)

    # Load the last sent offers
    stored_offers = ending_offers.get_stored_offers()

    new_offer_headers = set()
    price_changed_headers = set()

    for offer in new_offers:
        header = offer['header']
        if not first_run:
            if header not in stored_offers:
                new_offer_headers.add(header)
            elif offer['price'] != stored_offers[header]['price']:
                price_changed_headers.add(header)

    # Send email if there are new offers or price changes, or if it's the first run
    if new_offer_headers or price_changed_headers or first_run:
        ending_offers.send_email(
            credentials['sender'], credentials['password'], credentials['recipient'],
            new_offers, new_offer_headers, price_changed_headers, stored_offers
        )
        ending_offers.store_offers(new_offers)
    else:
        logging.info("Email not sent due to no new offers or price changes")


    # Happy Hours
    happy_hours = HappyHours()
    new_happy_hours_offers = happy_hours.scrape_offers()

    # Assuming the structure of happy hours offers is similar to ending offers
    happy_hours_first_run = not os.path.exists(happy_hours.stored_offers_file)
    stored_happy_hours_offers = happy_hours.get_stored_offers()

    new_happy_hours_offer_headers = set()
    for offer in new_happy_hours_offers:
        header = offer['header']
        if not happy_hours_first_run and header not in stored_happy_hours_offers:
            new_happy_hours_offer_headers.add(header)

    # Send email if there are new happy hours offers or if it's the first run
    if new_happy_hours_offer_headers or happy_hours_first_run:
        happy_hours.send_email(
            credentials['sender'], credentials['password'], credentials['recipient'],
            new_happy_hours_offers, new_happy_hours_offer_headers, set(), stored_happy_hours_offers
        )
        happy_hours.store_offers(new_happy_hours_offers)


if __name__ == "__main__":
    main()
