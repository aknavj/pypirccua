import sys
import re

# parses *.db file - card database file
class DbCardFile:
  
    def __init__(self, file_path):
        self.file_path = file_path
        self.card_data = {
            "header": None,
            "generation": None,
            "architecture": None,
            "logical_layers": [],
            "subunits": [],
            "physical_layers": []
        }

    def parse_file(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("H") or line.startswith("E"):
                    continue

                prefix = line[0]
                if prefix == "P":
                    self.parse_header(line)
                elif prefix == "G":
                    self.parse_generation(line)
                elif prefix == "A":
                    self.parse_architecture(line)
                elif prefix == "L" and "BIT" not in line:
                    self.parse_physical_layer(line)
                elif prefix == "S":
                    self.parse_subunits(line)
                elif prefix == "R":
                    self.parse_relay(line)

        return self.card_data

    def parse_header(self, line):
        match = re.match(r"PILPXIDB([0-9]+);(.*)", line)
        if match:
            version, card_info = match.groups()
            self.card_data["header"] = {"version": int(version), "card_info": card_info}

    def parse_generation(self, line):
        match = re.match(r"G;([0-9]+)", line)
        if match:
            self.card_data["generation"] = int(match.group(1))

    def parse_architecture(self, line):
        match = re.match(r"A;([0-9]+);([^;]+);([0-9]+);([^;]+)", line)
        if match:
            loops, description, num_loops, allocations = match.groups()
            allocations = list(map(int, allocations.split(",")))

            # store physical layers as loops
            self.card_data["physical_layers"] = [
                {"loop_id": i, "rows": allocations[i], "cols": allocations[i], "relays": {}}
                for i in range(int(num_loops))
            ]

            self.card_data["architecture"] = {
                "loops": int(loops),
                "description": description,
                "num_loops": int(num_loops),
                "allocations": allocations
            }

    def parse_physical_layer(self, line):
        pass  # note: not required, as physical layers are already handled in `parse_architecture`

    def parse_subunits(self, line):
        match = re.match(r"S;([0-9]+);([0-9]+);([0-9]+);([0-9]+);([0-9]+);([0-9]+);([^;]+)", line)
        if match:
            layer_id, sub_type, rows, cols, components, u2, description = match.groups()

            # normalize subunit ID: S;0 becomes S1
            subunit_id = int(layer_id) + 1

            self.card_data["subunits"].append({
                "layer_id": subunit_id,
                "type": int(sub_type),
                "rows": int(rows),
                "cols": int(cols),
                "num_components": int(components),
                "u2": int(u2),
                "description": description,
                "relays": {}
            })

    def parse_relay(self, line):
        match = re.match(r"R;([LP]);([SL][0-9]+)BIT([0-9]+);([0-9]+)", line)
        if match:
            layer_type, subunit_or_layer, bit, count = match.groups()
            bit = int(bit)
            count = int(count)

            # logical layer relay
            if layer_type == "L":  
                subunit_id = int(re.sub(r"[^0-9]", "", subunit_or_layer)) 
                for subunit in self.card_data["subunits"]:
                    if subunit["layer_id"] == subunit_id:
                        cols = subunit["cols"]
                        row = (bit - 1) // cols
                        col = (bit - 1) % cols
                        subunit["relays"][(row, col)] = count
                        break

            # physical layer relay
            elif layer_type == "P":  
                loop_id = int(re.sub(r"[^0-9]", "", subunit_or_layer)) 
                for loop in self.card_data["physical_layers"]:
                    if loop["loop_id"] == loop_id:
                        loop["relays"][(bit - 1, 0)] = count  # Store relay count for the bit number
                        break
