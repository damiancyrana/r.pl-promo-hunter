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


    def send_email(self, sender, password, recipient):
        offers = self.scrape_offers()

        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = recipient

        current_date = datetime.now().strftime('%Y-%m-%d')
        subject = f"Ending Offers - {current_date}"
        message['Subject'] = Header(subject, 'utf-8')

        body = "<h1>Rainbow Ending Offers</h1>"
        for offer in offers:
            body += f"<h2>{offer['header']}</h2>"
            body += f"<p>Location: {offer['location']}</p>"
            body += f"<p>Price: {offer['price']} PLN</p>"
            body += f"<p>Link: <a href='{offer['link']}'>View Offer</a></p>"
            body += "<hr>"

        message.attach(MIMEText(body, 'html'))

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