import requests

class Element14API:
    def __init__(self, api_key, search_market):
        self.api_key = api_key
        self.search_market = search_market
        self.base_url = "https://api.element14.com/catalog/products"

    def extract_component_data(self, component_json, partNumber):
        if component_json["translatedManufacturerPartNumber"] == partNumber:
            first_product = component_json
            manufacturer = first_product.get("brandName", "Unknown Manufacturer")
            prices = {}

            for price_info in first_product.get("prices", []):
                from_qty = price_info.get("from", 0)
                price = price_info.get("cost", 0)
                prices[from_qty] = price

            stock = first_product.get("stock", {})
            availability = stock.get("level", 0)
            lifeCycleStatus = first_product.get("productStatus", 0)
            return {
                "availability":  availability,
                "manufacturer": manufacturer,
                "prices": prices,
                "lifeCycleStatus": lifeCycleStatus,
            }
        return None

    def parseComponentResponse(self, component_result, partNumber, quantity):
        components = []

        if component_result["manufacturerPartNumberSearchReturn"]["numberOfResults"] > 0:
            optimal_part = None
            min_difference = float('inf')

            for part in component_result["manufacturerPartNumberSearchReturn"]["products"]:
                min_order_qty = part.get("translatedMinimumOrderQuality")

                if min_order_qty < quantity:
                    component_data = self.extract_component_data(part, partNumber)
                    if component_data:
                        components.append(component_data)
                        return components
                else:
                    difference = abs(min_order_qty - quantity)
                    if difference < min_difference:
                        min_difference = difference
                        optimal_part = part

            if optimal_part:
                component_data = self.extract_component_data(optimal_part, partNumber)
                if component_data:
                    components.append(component_data)

        return components


    def search_partNumber(self, partNumber, quantity):
        url = f"{self.base_url}?term=manuPartNum:{partNumber}&storeInfo.id={self.search_market}&resultsSettings.offset=0&resultsSettings.numberOfResults=1&resultsSettings.refinements.filters=&resultsSettings.responseGroup=medium&callInfo.omitXmlSchema=false&callInfo.callback=&callInfo.responseDataFormat=json&callinfo.apiKey={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            if response.text:
                return self.parseComponentResponse(response.json(), partNumber, quantity)
            else:
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud: {e}")
            return None

    def get_price_for_quantity(self, component, quantity):
        prices = component.get("prices", {})

        # Convertir las claves de precios a enteros
        sorted_quantities = sorted(prices.keys(), key=lambda x: int(x))  # Ordenar cantidades disponibles

        applicable_price = None
        optimal_price_quantity = None
        recommended_units = quantity


        for q in sorted_quantities:
            if quantity >= int(q):  # Si la cantidad solicitada es mayor o igual a la cantidad en el precio
                applicable_price = prices[q]
            else:
                break

        if applicable_price is None:
            applicable_price = prices[sorted_quantities[0]]
            quantity = sorted_quantities[0]
            recommended_units = quantity

        unit_price = float(applicable_price)
        total_price = unit_price * quantity

        is_optimal = True
        recommended_price = unit_price
        for q in sorted_quantities:
            if int(q) > quantity:
                future_unit_price = float(prices[q])
                future_total_price = future_unit_price * int(q)
                if future_total_price < total_price:
                    is_optimal = False
                    optimal_price_quantity = int(q)
                    recommended_units = optimal_price_quantity
                    recommended_price = future_unit_price
                    break

        return {
            "unit_price": unit_price,
            "total_price": total_price,
            "is_optimal": is_optimal,
            "recommended_units": recommended_units,
            "recommended_price": recommended_price,
            "message": "Optimal price found" if is_optimal else f"Better price available for {optimal_price_quantity} units."
        }