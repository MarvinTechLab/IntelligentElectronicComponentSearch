import json


markets            = ["MOUSER", "DIGIKEY", "TME", "ELEMENT14"]
attributes         = ["STOCK", "RECOMMENDED UNIT PRICE", "RECOMMENDED TOTAL PRICE", "RECOMMENDED QUANTITY", "INFO", "INFO_ALERT"]
attributes_visible = [1,1,1,1,1,0]


class ComponentClass:
    def __init__(self, part_number="", manufacturer="", units_per_board = 0, total_units_per_board=0):
        self.part_number = part_number
        self.manufacturer = manufacturer
        self.units_per_board = units_per_board
        self.total_units_per_board = total_units_per_board
        self.market_info = {}

    # Crea un market_ingo
    def create_market_info(self, stock, recommended_unit_price, recommended_total_price, recommended_quantity, info, info_alert):
        market_info = {}
        market_info["STOCK"] =  str(stock)
        market_info["RECOMMENDED UNIT PRICE"] = str(recommended_unit_price)
        market_info["RECOMMENDED TOTAL PRICE"] = str(recommended_total_price)
        market_info["RECOMMENDED QUANTITY"] = str(recommended_quantity)
        market_info["INFO"] = info
        market_info["INFO_ALERT"] = info_alert
        return market_info

    # Añade la informacion de un market a la clase
    def add_market_info(self, market_name, market_info):
        if market_name not in markets:
            raise ValueError(f"Market '{market_name}' is not supported. Supported markets are: {markets}")

        if market_name not in self.market_info:
            self.market_info[market_name] = {}

        self.market_info[market_name].update(market_info)

    # Devuelve la informacion de un market
    def get_market_info(self, market_name):
        if market_name not in self.market_info:
            #raise KeyError(f"Market '{market_name}' does not exist in the market info.")
            # Recorre los attributos
            marketInfo = {}
            for idx, attribute in enumerate(attributes):
                # Generar un nombre único combinando market y attribute
                marketInfo[attribute] = ""

            return marketInfo
        return self.market_info[market_name]


    def to_dict(self):
        """Convierte el objeto en un diccionario."""
        return {
            "part_number": self.part_number,
            "manufacturer": self.manufacturer,
            "units_per_board": self.units_per_board,
            "total_units_per_board": self.total_units_per_board,
            "market_info": self.market_info
        }

    def to_json(self):
        """Convierte el objeto a una cadena JSON."""
        componentData = self.to_dict()
        #jsonData =  json.dumps(componentData, indent=4)
        return componentData

    @staticmethod
    def from_dict(data):
        """Crea un objeto ComponentClass a partir de un diccionario."""
        component = ComponentClass(
            part_number=data.get("part_number", ""),
            manufacturer=data.get("manufacturer", ""),
            units_per_board=data.get("units_per_board", 0),
            total_units_per_board=data.get("total_units_per_board", 0)
        )
        component.market_info = data.get("market_info", {})
        return component

    @staticmethod
    def from_json(json_data):
        """Crea un objeto ComponentClass a partir de una cadena JSON."""
        data = json.loads(json_data)
        return ComponentClass.from_dict(data)
