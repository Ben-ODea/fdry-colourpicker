import tensorflow as tf
import tensorflow_hub as hub
import fcntl
import time
import html
import csv

### GLOBALS ###

# The anchors are about the midpoints of four quadrants defined by two axes: acc/decel and life/physical sciences.
anchors = {
    "A": "I am an accelerationist with a love of the physical sciences. I am an advocate for the rapid advancement of technological progress, seeking to propel humanity forward through the relentless pursuit of innovation and understanding of physics, mathematics, hardware engineering, and related disciplines.",
    "B": "I am an accelerationist with a love of the life sciences. I am an advocate for the rapid advancement of technological progress in biology and life itself.",
    "C": "I am a decelerationist with a love of the physical sciences. I am an advocate for the slow and careful advancement of technological progress, seeking to propel humanity forward through the relentless pursuit of innovation and understanding of physics, mathematics, hardware engineering, and related disciplines.",
    "D": "I am a decelerationist with a love of the life sciences. I am an advocate for the slow and careful advancement of technological progress in biology and life itself."
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
    "A": model([anchors["A"]]),
    "B": model([anchors["B"]]),
    "C": model([anchors["C"]]),
    "D": model([anchors["D"]])
}




### FUNCTIONS ###

def handle_form(user: dict):
    """
    Takes a dictionary of user data and returns a dictionary of the form {name: ..., workplace: ..., answer: ..., RGB: ...}.
    """

    # Get the distances and RGB encoding for the user's answer
    distances = answer_to_RGB(user["answer"])
    RGB = make_rgb_vibrant(distances)

    # Save the data to a CSV file
    user["A"] = distances[0]; user["B"] = distances[1]; user["C"] = distances[2]; user["D"] = distances[3]
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
    Takes a string and returns the distances between answer and anchor points.
    """

    embedding = model([answer])

    RGB = []
    for colour in ["A", "B", "C", "D"]:
        distance = tf.norm(embedding - embeddings[colour], ord="euclidean")
        RGB.append(distance) 

    return RGB


def make_rgb_vibrant(RGB):
    """
    Takes a list of distances and selects a coloured quadrant based on the distances.
    """

    # Get the closest anchor
    nearest_anchor = RGB.index(min(RGB))

    # Return the colour related to the closest anchor
    if nearest_anchor == 0: # nearest anchor is acc/physical = watermelon
        return [255, 40, 96]
    elif nearest_anchor == 1: # nearest anchor is acc/life = leaf
        return [0, 181, 143]
    elif nearest_anchor == 2: #nearest anchor is dec/physical = lemon
        return [255, 180, 0]
    else: # nearest anchor is dec/life = grape
        return [92, 64, 138]
    

### TESTING ###

# If this file is run directly (rather than routes.py importing it), run a test mode
if __name__ == "__main__":
    print("[*] Testing mode. Enter a paragraph to get its RGB encoding. Ctrl+C to terminate.")
    while True:
        answer = input(">>> ")
        distances = answer_to_RGB(answer)
        colour = make_rgb_vibrant(distances)
        print("[+] Normalised colour array is:", colour)
        print("[+] distances were:",distances)