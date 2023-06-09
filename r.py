import json
import smtplib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from email.header import Header
from urllib.parse import urljoin
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EndingOffers:
    """A class to scrape and send offers from https://r.pl/koncoweczka via email"""

    def __init__(self):
        self.url_for_ending_offers = "https://r.pl/koncoweczka"
        self.email_template_file = "email_template.html"


    def scrape_offers(self):
        response = requests.get(self.url_for_ending_offers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all div elements with class "bloczek__wrapper"
        wrappers = soup.find_all('div', class_='bloczek__wrapper')

        # List to store the offers
        offers = []

        for wrapper in wrappers:
            header_element = wrapper.find('p', class_='bloczek__tytul')
            link_element = wrapper.find('a')
            price_element = wrapper.find('span', class_='bloczek__cena')
            location_element = wrapper.find('span', class_='bloczek__lokalizacja--text')

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
        with open(self.email_template_file, 'r') as file:
            html_template = file.read()

        offers_html = ""
        for offer in offers:
            offer_html = """
            <div class="offer">
                <h2>{header}</h2>
                <p>Location: {location}</p>
                <p>Price: {price} PLN</p>
                <p>Link: <a href="{link}">View Offer</a></p>
                <hr>
            </div>
            """.format(
                header=offer['header'],
                location=offer['location'],
                price=offer['price'],
                link=offer['link']
            )
            offers_html += offer_html

        message = html_template.replace('{{offers}}', offers_html)
        return message


    def send_email(self, sender, password, recipient):
        offers = self.scrape_offers()
        html_message = self.generate_html_message(offers)

        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = recipient

        current_date = datetime.now().strftime('%Y-%m-%d')
        subject = f"Rainbow Ending Offers - {current_date}"
        message['Subject'] = Header(subject, 'utf-8')

        message.attach(MIMEText(html_message, 'html'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, message.as_string())
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")


with open('credentials.json') as json_file:
    credentials = json.load(json_file)

ending = EndingOffers()
ending.send_email(credentials['sender'], credentials['password'], credentials['recipient'])
