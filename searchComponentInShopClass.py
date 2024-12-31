#IMPORT DE LAS APIS
from APIs import mouserApi
from APIs import  element14Api
from APIs import  tmeApi
from APIs import  digikeyApi

import componentClass


class SearchComponentInShop:
    def __init__(self):
        self.active_markets = {market: False for market in componentClass.markets}
        self.market_tokens = {market: None for market in componentClass.markets}

    def init_mouser(self, token):
        self.market_tokens["MOUSER"] = token
        self.active_markets["MOUSER"] = True
        self.mouser_api = mouserApi.MouserAPI(token)

    def init_digikey(self, clientID, clientSecret, currency, language, localsite):
        self.market_tokens["DIGIKEY"] = clientID
        self.active_markets["DIGIKEY"] = True
        self.digiKey_api = digikeyApi.DigiKeyAPI(clientID, clientSecret, currency,  language, localsite)

    def init_tme(self, token, secret, country, language, currency):
        self.market_tokens["TME"] = token
        self.active_markets["TME"] = True

        self.tme_api = tmeApi.TmeApi(token, secret, country, language, currency)

    def init_element14(self, token, element14_market):
        self.market_tokens["ELEMENT14"] = token
        self.active_markets["ELEMENT14"] = True
        self.element14_api = element14Api.Element14API(token, element14_market)

    def search_part_number(self, market_name, part_number, quantity):
        if (self._validate_market(market_name) == False):
            return 0

        if market_name == "MOUSER":
            return self._search_part_number_mouser(part_number, quantity)
        elif market_name == "DIGIKEY":
            return self._search_part_number_digikey(part_number, quantity)
        elif market_name == "TME":
            return self._search_part_number_tme(part_number, quantity)
        elif market_name == "ELEMENT14":
            return self._search_part_number_element14(part_number, quantity)
        else:
            raise ValueError(f"Market '{market_name}' is not implemented.")

    def get_price_per_quantity(self, market_name, part_number, quantity):
        if (self._validate_market(market_name) == False):
            return 0

        if market_name == "MOUSER":
            return self._get_price_per_quantity_mouser(part_number, quantity)
        elif market_name == "DIGIKEY":
            return self._get_price_per_quantity_digikey(part_number, quantity)
        elif market_name == "TME":
            return self._get_price_per_quantity_tme(part_number, quantity)
        elif market_name == "ELEMENT14":
            return self._get_price_per_quantity_element14(part_number, quantity)
        else:
            raise ValueError(f"Market '{market_name}' is not implemented.")

    def _validate_market(self, market_name):
        if market_name not in componentClass.markets:
            raise ValueError(f"Market '{market_name}' is not supported.")
        if not self.active_markets[market_name]:
            return False
        return True

    def _search_part_number_mouser(self, part_number, quantity):
        return self.mouser_api.search_partNumber(part_number, quantity)

    def _search_part_number_digikey(self, part_number, quantity):
        return self.digiKey_api.search_partNumber(part_number, quantity)

    def _search_part_number_tme(self, part_number, quantity):
        return self.tme_api.search_partNumber(part_number, quantity)

    def _search_part_number_element14(self, part_number, quantity):
        return self.element14_api.search_partNumber(part_number, quantity)

    def _get_price_per_quantity_mouser(self, part_number_info, quantity):
        return self.mouser_api.get_price_for_quantity(part_number_info, quantity)

    def _get_price_per_quantity_digikey(self, part_number_info, quantity):
        return self.digiKey_api.get_price_for_quantity(part_number_info, quantity)

    def _get_price_per_quantity_tme(self, part_number_info, quantity):
        return self.tme_api.get_price_for_quantity(part_number_info, quantity)

    def _get_price_per_quantity_element14(self, part_number_info, quantity):
        return self.element14_api.get_price_for_quantity(part_number_info, quantity)
