
import requests
from .models import *

def fetch_and_save_promo():
    url = 'API_URL'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        tel = data.get('tel')
        promo_code = data.get('promo')

        promo, created = Promo.objects.get_or_create(tel=tel)
        promo.sent_count += 1
        promo.save()

        promo_entry = PromoEntry.objects.create(promo=promo, code=promo_code)
        return promo_entry
    else:
        return None
