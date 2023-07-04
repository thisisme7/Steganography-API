from PIL import Image
import base64

class Key:
    key = int
    attr = 0

def Embedder(picture, textfile):
    # one letter character is 1 byte large. One pixel contains 24 bits (3 bytes) for RGB
    image = Image.open("images/"+picture).convert('RGB') # image from customer
    text_message = open("messages/"+textfile).read() # message from customer
    message = base64.b64encode(text_message.encode("utf-8")).decode("utf-8")
    message_bits = ''.join(format(ord(char), '08b') for char in message) # disamble message to bits
    Key.key = len(message_bits) # message lenght in bits
    
    if len(message_bits) > ((image.size[0] * image.size[1]) * 3):
        raise ValueError("Message is larger than the image!")
    else:
        image_pixels = list(image.getdata())
        custom_pixels = image_pixels[:len(message_bits) // 3] # list of required pixels

        # Iterates through the required pixels for message
        bitindex = 0
        for pix in range(len(custom_pixels)):
            pixel = list(custom_pixels[pix]) # convert tuple to list
            for channel in range(len(pixel)):
                pixel[channel] = (pixel[channel] & 0xFE) | int(message_bits[bitindex]) # edit LSB
                bitindex += 1
                
            image_pixels[pix] = tuple(pixel)
                
        modified_image = Image.new(image.mode, image.size)
        modified_image.putdata(image_pixels)
        
        Key.attr+=1
        modified_image.save("modified/steg"+str(Key.attr)+picture)
        
        return str(Key.key), "steg"+str(Key.attr)+picture
        
        
def Extractor(picture, key):
    
    modified_image = Image.open("storage/"+picture)
    
    key_index = 0
    extracted_bits = ""  # Store the extracted bits of the message
    for pixel in modified_image.getdata():
        for channel in pixel:
            if key_index < int(key):
                extracted_bits += str(channel & 0x01)
                key_index+=1
    
    # Convert the extracted bits back into characters
    encoded_message = ""
    for i in range(0, len(extracted_bits), 8):
        byte = extracted_bits[i:i+8]
        encoded_message += chr(int(byte, 2))  # Convert each 8-bit sequence into a character using its ASCII value
    
    # decode base64 message here
    try:
        plainmessage = base64.b64decode(encoded_message).decode("utf-8")
        return plainmessage
    except Exception:
        error_message = "Invalid key"
        return error_message
    
