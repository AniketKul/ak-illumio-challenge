import csv
import random

class FlowLogAnalytics:
    def __init__(self):
        self.lookup_table = {} # map: (dstport, protocol) -> randomly generated tag
        self.tag_count = {} # map: randomly generated tag -> count
        self.lookup_size = 10000 # because the lookup file can have up to 10000 mappings 
        self.port_protocol_count = {} # map: (port, protocol) -> count
        self.protocol_map = {
            '6': 'tcp',
            '17': 'udp',
        } # https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
        # can be extended to include others like IGP, ICMP etc.
        
    def writeTagCount(self, output_file):
        if not output_file:
            return f'output_file does not exist to write tag count: {output_file}'
        
        header = ['tag', 'count']

        with open(output_file, 'w') as out_f:
            writer_obj = csv.writer(out_f)
            writer_obj.writerow(header)
            for tag, count in self.tag_count.items():
                writer_obj.writerow([tag, count])
    
    def writePortProtocolCombiCount(self, output_file):
        if not file_path:
            return f'output_file does not exist to write port-protocol combi count: {output_file}'
        
        header = ['Port', 'Protocol', 'Count']

        with open(output_file, 'a') as out_f:
            writer_obj = csv.writer(out_f)
            writer_obj.writerow(header)
            for (port, protocol), count in self.port_protocol_count.items():
                writer_obj.writerow([port, protocol, count])
    
    def generateTag(self, dstport, protocol):
        num = random.randint(0, self.lookup_size) # because the lookup table can have 10000 mappings. covering worst case.
        return f'sv_{protocol}{dstport}_p{num}'
    
    def processFlowLogData(self, file_path):
        if not file_path:
            return f'file_path does not exist: {file_path}'

        lookup_file_path = 'lookup.csv'
        header = ['dstport', 'protocol', 'tag']

        with open(file_path, 'r') as file:
            with open(lookup_file_path, 'w') as lf:
                writer_obj = csv.writer(lf)
                writer_obj.writerow(header)
            for line in file:
                columns = line.strip().split()
                if len(columns) < 7:
                    continue  # skip incorrect lines
                dstport = columns[6].strip() if columns[6].strip().isalnum() else ''
                # making it case insensitive
                protocol = columns[7].strip().lower() if columns[7].strip().isalnum() else ''
                protocol = self.protocol_map[protocol] if protocol in self.protocol_map else ''

                # print(dstport, protocol)

                if dstport == '' or protocol == '':
                    tag = 'untagged'

                if (dstport, protocol) not in self.lookup_table:
                    if dstport and protocol:
                        tag = self.generateTag(dstport, protocol)
                    self.lookup_table[(dstport, protocol)] = tag
                
                if (dstport, protocol) in self.lookup_table:
                    tag = self.lookup_table[(dstport, protocol)]
                
                self.tag_count[tag] = self.tag_count.get(tag, 0) + 1
                self.port_protocol_count[(dstport, protocol)] = self.port_protocol_count.get((dstport, protocol), 0) + 1

                with open(lookup_file_path, 'a') as lf:
                    writer_obj = csv.writer(lf)
                    writer_obj.writerow([dstport, protocol, tag])
    
    def generateOutput(self, file_path):
        self.processFlowLogData(file_path)
        output_file = 'output.csv'
        self.writeTagCount(output_file)
        self.writePortProtocolCombiCount(output_file)

if __name__ == "__main__":
    fla = FlowLogAnalytics()
    file_path = 'flow-log-data.csv'
    fla.generateOutput(file_path)