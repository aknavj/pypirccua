from pidbcard import *

card = PiDbCard("G385_60-891-006,410155,1.00.db")
data = card.parse_file()

print(data["header"]) 
print(data["generation"])
print(data["architecture"])
print(data["subunits"])
print(data["physical_layers"])
