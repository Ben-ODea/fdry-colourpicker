import tensorflow as tf
import tensorflow_hub as hub
import fcntl
import time
import html
import csv

### GLOBALS ###

# The anchors are the three main roles in a company: R&D, Growth, and Branding
anchors = {
    "R": "I am a software engineer, developer, and technical expert.",
    "G": "I enjoy events, organising, and networking to create new sales and hiring opportunities.",
    "B": "I take care of the marketing, branding, and design of the product."
}

# Load the model from disk or download it if it doesn't exist
print("[+] Loading model...")
try: model = tf.saved_model.load("./backend/model")
except: 
    print("[-] Model not found on disk. Please be patient while it downloads...")
    model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
    tf.saved_model.save(model, "./backend/model")
print("[+] Model loaded.")

# Precompute the embeddings of the anchors
embeddings = {
    "R": model([anchors["R"]]),
    "G": model([anchors["G"]]),
    "B": model([anchors["B"]])
}


### FUNCTIONS ###

def handle_form(user: dict):
    """
    Takes a dictionary of user data and returns a dictionary of the form {name: ..., workplace: ..., answer: ..., RGB: ...}.
    """

    # Get the RGB encoding of the answer
    RGB = answer_to_RGB(user["answer"])
    RGB = make_rgb_vibrant(RGB)

    # Save the data to a CSV file
    user["R"] = RGB[0]; user["G"] = RGB[1]; user["B"] = RGB[2]
    user["RGB"] = "#%02x%02x%02x" % tuple(RGB)
    save_to_csv(user)

    # Return the RGB encoding for the client - format it as hex for easy use in CSS
    return {"name": html.escape(user["name"]),"RGB": user["RGB"]}


def save_to_csv(data: dict):
    """
    Takes a set of data and saves it to data/responses.csv.
    """

    # Sanitise and escape illegal characters
    for field in data:
        data[field] = str(data[field]).strip()
        for illegal in ["\n", "\r", "\t"]:
            data[field] = data[field].replace(illegal, " ")

    # Wait until the file is unlocked before writing to it (async safe)
    while True:
        try:
            with open("data/responses.csv", "a") as f:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)  
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerow(data.values())
                fcntl.flock(f, fcntl.LOCK_UN)
            break  
        except BlockingIOError:
            print("[-] File is locked, waiting...")
            time.sleep(1) 


def answer_to_RGB(answer):
    """
    Takes a string and returns a list of three integers between 0 and 255 representing the RGB encoding of the answer.
    """

    embedding = model([answer])

    RGB = []
    for colour in ["R", "G", "B"]:
        distance = tf.math.reduce_sum(tf.math.square(tf.math.subtract(embedding, embeddings[colour])))
        distance = min(2, distance) / 2 # Cap the distance at 2
        distance = pow(distance, 2) # Square the distance to make it more extreme
        distance = 255 * (1 - distance) # Invert the distance and scale it to 0-255
        RGB.append(int(distance)) 

    return RGB


def make_rgb_vibrant(RGB):
    """
    Takes a list of three integers between 0 and 255 representing the RGB encoding of the answer and returns a list of three integers between 0 and 255 representing the RGB encoding of the answer, with the colour made more vibrant.
    """

    # Get the maximum value of the three colours
    max_colour = max(RGB)

    # If the maximum value is 255, return the original colour
    if max_colour == 255:
        return RGB

    # Otherwise, scale the colours up to 255
    else:
        return [int(255 * (colour / max_colour)) for colour in RGB]


### TESTING ###

# If this file is run directly (rather than routes.py importing it), run a test mode
if __name__ == "__main__":
    print("[*] Testing mode. Enter a paragraph to get its RGB encoding. Ctrl+C to terminate.")
    while True:
        answer = input(">>> ")
        RGB = answer_to_RGB(answer)
        print("[+] Normalised colour array is:", RGB)


