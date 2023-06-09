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

        # Find all div elements with class "bloczki-lp__content"
        divs = soup.find_all('div', class_='bloczki-lp__content')

        # List to store the offers
        offers = []

        # Iterate over each div
        for div in divs:
            # Find all header elements within the div
            header_elements = div.find_all('div', class_='bloczek__naglowek')
            # Find all link elements within the div
            link_elements = div.find_all('a')
            # Find all price elements within the div
            price_elements = div.find_all('span', class_='bloczek__cena h1')
            # Find all location elements within the div
            location_elements = div.find_all('span', class_='bloczek__lokalizacja--text')

            # Prepare an offer with header, link, price, and location
            for header, link, price, location in zip(header_elements, link_elements, price_elements, location_elements):
                # Combine the relative link with the base URL
                absolute_link = urljoin(self.url, link['href'])

                offer = {
                    'header': header.text.strip(),
                    'location': location.text.strip(),
                    'price': price.text.strip(),
                    'link': absolute_link,
                }
                offers.append(offer)

        return offers

    def send_email(self, sender, password, recipient):
        offers = self.scrape_offers()

        # Create the message
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = recipient

        # Add the date to the subject
        current_date = datetime.now().strftime('%Y-%m-%d')
        subject = f"Ending Offers - {current_date}"
        message['Subject'] = Header(subject, 'utf-8')

        # Create the HTML content for the email body
        body = "<h1>Rainbow Ending Offers</h1>"
        for offer in offers:
            body += f"<h2>{offer['header']}</h2>"
            body += f"<p>Location: {offer['location']}</p>"
            body += f"<p>Price: {offer['price']} PLN</p>"
            body += f"<p>Link: <a href='{offer['link']}'>View Offer</a></p>"
            body += "<hr>"

        # Attach the HTML content to the message
        message.attach(MIMEText(body, 'html'))

        # Send the email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, message.as_string())
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

# Load email credentials from JSON file
with open('credentials.json') as json_file:
    credentials = json.load(json_file)


ending = EndingOffers()
ending.send_email(credentials['sender'], credentials['password'], credentials['recipient'])
