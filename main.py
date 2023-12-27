import heapq
import os
import typer
from InquirerPy import prompt

app = typer.Typer()
heap = []
codes = {}
reverse_codes = {}

class HeapNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    
    def __lt__(self, other):
        return self.freq < other.freq

    def __eq__(self, other):
        if (other == None):
            return False
        if (not isinstance(other, HeapNode)):
            return False
        return self.freg == other.freq

def get_frequency(text):
    frequency = {}
    for c in text:
        count = sum(map(lambda x: 1 if c in x else 0, text))
        frequency.update({c : count})
    return frequency

def create_priority_queue(frequency):
    for key in frequency:
        node = HeapNode(key, frequency[key])
        heapq.heappush(heap, node)

def merge_codes(heap):
    while(len(heap)>1):
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = HeapNode(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged) 

def generate_binary_codes(node, current_node):
    if (node is None):
        return
    if (node.char is not None):
        codes[node.char] = current_node
        reverse_codes[current_node] = node.char
    generate_binary_codes(node.left , current_node + "0")
    generate_binary_codes(node.right , current_node + "1")

def make_codes():
    root =  heapq.heappop(heap)
    current_code = ""
    generate_binary_codes(root, current_code)

def get_encoded_text(text):
    encoded_text = ""
    for character in text:
        encoded_text += codes[character]
    return encoded_text

def pad_encoded_text(encoded_text):
    extra_padding = 8 - len(encoded_text)%8
    for i in range(extra_padding):
        encoded_text += "0"
    padded_info = "{0:08b}".format(extra_padding)
    encoded_text = padded_info + encoded_text
    return encoded_text

def get_byte_array(padded_encoded_text):
    bArray =  bytearray()
    for i in range(0, len(padded_encoded_text), 8):
        byte  = padded_encoded_text[i:i+8]
        bArray.append(int(byte, 2))
    return bArray



def remove_padding(bit_string):
    padded_info = bit_string[:8]
    extra_padding = int(padded_info,2)
    bit_string = bit_string[8:]
    encoded_text = bit_string[:-1*extra_padding]
    return encoded_text

def decode_text(encode_text):
    current_code = ""
    decoded_text = ""
    for bit in encode_text:
        current_code += bit
        if  (current_code in reverse_codes):
            character = reverse_codes[current_code]
            decoded_text += character
            current_code = ""
    return decoded_text

@app.command("compress")
def compress():
    questions = [
    {
    'type': 'input',
    'name': 'path',
    'message': 'Enter the document path',
    }
    ]
   
    path = prompt(questions)
    path = path["path"]

    filename, file_extension = os.path.splitext(path)
    output_path = filename + ".bin"

    with open(path, 'r') as file, open(output_path, 'wb') as output:
        text = file.read()
        text = text.rstrip()
        
        frequency = get_frequency(text)
        create_priority_queue(frequency)
        merge_codes(heap)
        make_codes()
        encoded_text = get_encoded_text(text)
        padded_encoded_text = pad_encoded_text(encoded_text)

        b = get_byte_array(padded_encoded_text)
        output.write(bytes(b))
    print("Compressed")
    return output_path

@app.command("decompress")
def decompress():
    questions = [
    {
    'type': 'input',
    'name': 'path',
    'message': 'Enter the document path',
    }
    ]
   
    input_path = prompt(questions)
    input_path= input_path["path"]

    filename , file_extension = os.path.splitext(input_path)
    output_path = filename + "_decompressed" + ".txt"

    with open(input_path, "rb" ) as file, open(output_path, "w") as output:
        bit_string = ""
        byte =  file.read(1)
        while (len(byte)>0):
            byte = ord(byte)
            bits = bin(byte)[2:].rjust(8,'0')
            bit_string += bits
            byte = file.read(1)
        encoded_text = remove_padding(bit_string)
        decoded_text = decode_text(encoded_text)
        output.write(decoded_text)
    print("Decompressed")

if __name__ == '__main__':
    app()

