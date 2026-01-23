"""Module for loading circuit data from CSV files"""
import csv

class DataLoader:
    """Handles loading of chip, connection, and datasheet data from CSV files"""
    
    @staticmethod
    def load_datasheets(datasheet_csv):
        """Load chip datasheet information from CSV file"""
        datasheets = {}
        with open(datasheet_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                chip_type = row['chip_type']
                gate_num = int(row['gate_num'])
                
                if chip_type not in datasheets:
                    datasheets[chip_type] = {}
                
                datasheets[chip_type][gate_num] = {
                    'input_pins': [int(p.strip()) for p in row['input_pins'].split(',')],
                    'output_pin': int(row['output_pin']),
                    'gate_type': row['gate_type'],
                    'vcc_pin': int(row['vcc_pin']),
                    'gnd_pin': int(row['gnd_pin']),
                    'total_pins': int(row['total_pins'])
                }
        return datasheets
    
    @staticmethod
    def load_chips(chips_csv, datasheets):
        """Load chip definitions from CSV file"""
        chips = {}
        with open(chips_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                chip_id = row['chip_id']
                chip_type = row['chip_type']
                gate_num = int(row['gate_num'])
                layer = int(row['layer'])
                
                # Get datasheet info for this chip
                if chip_type in datasheets and gate_num in datasheets[chip_type]:
                    gate_data = datasheets[chip_type][gate_num]
                    chips[chip_id] = {
                        'chip_type': chip_type,
                        'gate_num': gate_num,
                        'layer': layer,
                        'gate_type': gate_data['gate_type'],
                        'vcc_pin': gate_data['vcc_pin'],
                        'gnd_pin': gate_data['gnd_pin']
                    }
        return chips
    
    @staticmethod
    def load_connections(connections_csv):
        """Load connections from CSV file, separating inputs/outputs from chip-to-chip connections"""
        connections = []
        inputs = []
        outputs = []
        seen_inputs = set()
        
        with open(connections_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['from_chip'].lower() == 'input':
                    # Input connection
                    input_name = row['from_pin']
                    # Add to inputs list for drawing box if new
                    if input_name not in seen_inputs:
                        seen_inputs.add(input_name)
                        inputs.append({
                            'name': input_name
                        })
                    
                    # ALWAYS add the connection
                    connections.append({
                        'from_chip': 'input',
                        'from_pin': input_name,
                        'to_chip': row['to_chip'],
                        'to_pin': int(row['to_pin'])
                    })
                    
                elif row['to_chip'].lower() == 'output':
                    # Output connection
                    output_name = row['to_pin']
                    outputs.append({
                        'name': output_name,
                        'from_chip': row['from_chip'],
                        'from_pin': int(row['from_pin'])
                    })
                    
                    # Add connection
                    connections.append({
                        'from_chip': row['from_chip'],
                        'from_pin': int(row['from_pin']),
                        'to_chip': 'output',
                        'to_pin': output_name
                    })
                else:
                    # Regular chip-to-chip connection
                    connections.append({
                        'from_chip': row['from_chip'],
                        'from_pin': int(row['from_pin']),
                        'to_chip': row['to_chip'],
                        'to_pin': int(row['to_pin'])
                    })
        
        return connections, inputs, outputs
