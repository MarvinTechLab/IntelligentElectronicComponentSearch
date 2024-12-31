import requests

class MouserAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.mouser.com/api/v1/search/partnumber"

    def search_partNumber(self, part_number, quantity):
        url = f"{self.base_url}?apiKey={self.api_key}"

        payload = {
            "SearchByPartRequest": {
                "mouserPartNumber": part_number,
                "partSearchOptions": ""
            }
        }

        headers = {
            "Content-Type": "application/json",
            "accept": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Lanza una excepción si ocurre un error HTTP
            return self.parseComponentResponse(response.json(), part_number)

        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud: {e}")
            return None

    def extract_component_data(self, component_json, part_number):
        try:
            if (component_json.get("ManufacturerPartNumber", "Unknown") != part_number):
                return None

            availability = int(component_json.get("Availability", "0").split()[0])
            manufacturer = component_json.get("Manufacturer", "Unknown")
            lifeCycleStatus = component_json.get("LifecycleStatus", "Unknown")

            prices = {}
            currency = "USD"
            for price in component_json.get("PriceBreaks", []):
                quantity = price.get("Quantity", 0)
                price_value = price.get("Price", "0")
                prices[quantity] = price_value
                currency = price.get("Currency", "0")

            return {
                "availability": availability,
                "manufacturer": manufacturer,
                "prices": prices,
                "currency": currency,
                "lifeCycleStatus":  lifeCycleStatus,
            }
        except (ValueError, KeyError, TypeError) as e:
            print(f"Error al extraer datos del componente: {e}")
            return None

    def get_price_for_quantity(self, component, quantity):
        prices = component.get("prices", {})
        sorted_quantities = sorted(prices.keys(), key=lambda x: int(x))  # Ordenar cantidades disponibles

        applicable_price = None
        optimal_price_quantity = None
        recommended_units = quantity

        for q in sorted_quantities:
            if quantity >= int(q):
                applicable_price = prices[q]
            else:
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

        unit_price = float(applicable_price.replace(',', '.').split()[0])  # Convertir a float
        total_price = unit_price * quantity

        #  Get optimal prize
        is_optimal = True
        recommended_price = unit_price
        for q in sorted_quantities:
            if int(q) > quantity:
                future_unit_price = float(prices[q].replace(',', '.').split()[0])
                future_total_price = future_unit_price * int(q)
                if future_total_price < total_price:
                    is_optimal = False
                    optimal_price_quantity = int(q)
                    recommended_units = optimal_price_quantity
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

    def parseComponentResponse(self, component_result, part_number):
        components = []

        if component_result and "SearchResults" in component_result and component_result["SearchResults"]["Parts"]:
            for part in component_result["SearchResults"]["Parts"]:
                component_data = self.extract_component_data(part, part_number)
                if component_data:
                    components.append(component_data)
                    return components

        return components
