import requests


class DigiKeyAPI:
    def __init__(self, client_id, client_secret, currency, language, localsite):
        self.client_id =  client_id
        self.client_secret = client_secret
        self.localSite = localsite
        self.localCurrency = currency
        self._get_access_token()

    def _get_access_token(self):
        url = "https://api.digikey.com/v1/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"}

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            token_info = response.json()
            self.token_expirationIn = token_info['expires_in']
            self.tokenValue = token_info['access_token']
        else:
            print(f"Error: {response.status_code}, {response.text}")
            self.token_expirationIn = 0
            self.tokenValue = ""


    def search_partNumber(self, part_number, quantity):
        url = f"https://api.digikey.com/products/v4/search/{part_number}/productdetails"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer " + self.tokenValue,
            "X-DIGIKEY-Client-Id": self.client_id,
            "X-DIGIKEY-Locale-Site": self.localSite,
            "X-DIGIKEY-Locale-Currency": self.localCurrency,}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                product_details = response.json()
            else:
                print(f"Error: {response.status_code}, {response.text}")

            # Devolver el JSON completo de la respuesta
            return self.parseComponentResponse(response.json(), part_number)



        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud: {e}")
            return None

    def parseComponentResponse(self, component_result, part_number):
        components = []

        if (component_result
                and "Product" in component_result
                and isinstance(component_result["Product"], dict)  # Verificar que "Product" es un diccionario
        ):
            #for part in component_result["Product"]:
            component_data = self.extract_component_data(component_result["Product"], part_number)
            if component_data:
               components.append(component_data)
               return components

        return components


    def extract_component_data(self, component_json, part_number):
        try:
            #Check PN
            if (component_json["ManufacturerProductNumber"] != part_number):
                return None

            availability = component_json.get("QuantityAvailable", "0")
            manufacturer = component_json["Manufacturer"]["Name"]
            lifeCycleStatus =  component_json["ProductStatus"]["Status"]
            # Almacenar precios de forma dinámica
            prices = {}
            try:
                standard_pricing = component_json["ProductVariations"][1]['StandardPricing']
            except IndexError:
                standard_pricing = component_json["ProductVariations"][0]['StandardPricing']

            for price in standard_pricing:
                quantity = price.get("BreakQuantity", 0)
                price_value = price.get("UnitPrice", "0")
                prices[quantity] = price_value

            return {
                "availability": availability,
                "manufacturer": manufacturer,
                "prices": prices,
                "currency": self.localCurrency,
                "lifeCycleStatus":  lifeCycleStatus,
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


        unit_price = float(applicable_price)  # Convertir a float
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