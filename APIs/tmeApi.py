import requests
import collections
from urllib.parse import urlencode
import base64
import hmac
import hashlib

class TmeApi:
    def __init__(self, api_token, api_secret, country, language, currency):
        self._api_token = api_token
        self._api_secret = api_secret.encode()
        self._base_url = "https://api.tme.eu"
        self._country = country
        self._language = language
        self._currency = currency

    def __get_signature_base(self, url, params):
        params = collections.OrderedDict(sorted(params.items()))
        encoded_params = urlencode(params)
        signature_base = 'POST' + '&' + requests.utils.quote(url, safe='') + '&' + requests.utils.quote(encoded_params, safe='')
        return signature_base.encode()

    def __calculate_signature(self, url, params):
        hmac_value = hmac.new(self._api_secret, self.__get_signature_base(url, params), hashlib.sha1).digest()
        return base64.encodebytes(hmac_value).rstrip().decode()

    def __request(self, endpoint, params, format='json'):
        url = f"{self._base_url}{endpoint}.{format}"
        params['Token'] = self._api_token
        params['ApiSignature'] = self.__calculate_signature(url, params)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(url, headers=headers, data=params)
        return response

    def search_partNumber(self, part_number, quantity):
        parameters = {
            'SymbolList[0]': part_number,
            'Country':   self._country,
            'Language':  self._language,
            'Currency':  self._currency,
        }

        response = self.__request("/Products/GetPricesAndStocks", parameters)

        return self.parseComponentResponse(response.json(), part_number)

    def parseComponentResponse(self, component_result, part_number):
        components = []

        # verify data
        if (component_result
                and "Data" in component_result
                and isinstance(component_result["Data"], dict)
                and "ProductList" in component_result["Data"]
                and component_result["Data"]["ProductList"]
        ):
            for part in component_result["Data"]["ProductList"]:
                component_data = self.extract_component_data(part, part_number)
                if component_data:
                    components.append(component_data)
                    return components


        return components

    def extract_component_data(self, component_json, part_number):
        try:
            if (component_json.get("Symbol", "Unknown") != part_number):
                return None

            availability = int(component_json.get("Amount", "0"))
            prices = {}
            for price in component_json.get("PriceList", []):
                quantity = price.get("Amount", 0)
                price_value = price.get("PriceValue", "0")
                prices[quantity] = price_value

            return {
                "availability": availability,
                "manufacturer": None,
                "prices": prices,
                "currency": self._currency,
                "lifeCycleStatus": None,
            }
        except (ValueError, KeyError, TypeError) as e:
            print(f"Error al extraer datos del componente: {e}")
            return None

    def get_price_for_quantity(self, component, quantity):
        prices = component.get("prices", {})
        sorted_quantities = sorted(prices.keys(), key=lambda x: int(x))

        applicable_price = None
        optimal_price_quantity = None
        recommended_units = quantity

        for q in sorted_quantities:
            if quantity >= int(q):
                applicable_price = prices[q]
            elif applicable_price is None:
                applicable_price = prices[q]
                recommended_units = int(q)
                break

        if applicable_price is None:
            return {
                "unit_price": None,
                "total_price": None,
                "is_optimal": False,
                "recommended_units": None,
                "recommended_price": None,
                "message": "No price available for the given quantity."
            }

        unit_price = float(applicable_price)
        total_price = unit_price * recommended_units

        # Get optimal prize
        is_optimal = True
        recommended_price = unit_price
        for q in sorted_quantities:
            if int(q) > quantity:
                future_unit_price = float(prices[q])
                future_total_price = future_unit_price * int(q)
                if future_total_price < total_price:
                    is_optimal = False
                    optimal_price_quantity = int(q)
                    recommended_units = int(q)
                    recommended_price = future_unit_price
                    total_price = future_total_price
                    break

        return {
            "unit_price": unit_price,
            "total_price": total_price,
            "is_optimal": is_optimal,
            "recommended_units": recommended_units,
            "recommended_price": recommended_price,
            "message": "Optimal price found" if is_optimal else f"Better price available for {optimal_price_quantity} units."
        }
