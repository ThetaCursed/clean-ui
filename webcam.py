import json
import os
import sys
import subprocess
import cv2  # OpenCV for webcam input
from gradio_client import Client, handle_file
import tempfile
#python3 -m pip install opencv-python gradio-client

# Replace with the actual server URL if different
ip   = "127.0.0.1"
port = "8080"

# Define the user prompt (caption)
user_prompt = "Thoroughly and carefully describe this image."
#user_prompt = "Carefully describe the humans in the image their actions and their interactions."

output_file = "output.json"


def is_process_running(process_name):
    try:
        # Use ps and grep to check if the process is running
        output = subprocess.check_output(f"ps -A | grep -i {process_name}", shell=True, text=True)
        return process_name.lower() in output.lower()
    except subprocess.CalledProcessError:
        # grep returns non-zero exit code if no match is found
        return False

# Hyperparameters
temperature = 0.6
top_k = 50
top_p = 0.9
max_tokens = 100

# Parse command-line arguments (optional)
argumentStart = 1
if len(sys.argv) > 1:
    for i in range(0, len(sys.argv)):
        if sys.argv[i] == "--ip":
            ip = sys.argv[i+1]
            argumentStart += 2
        elif sys.argv[i] == "--port":
            port = sys.argv[i+1]
            argumentStart += 2
        elif sys.argv[i] == "--prompt":
            user_prompt = sys.argv[i+1]
            argumentStart += 2
        elif sys.argv[i] == "--temperature":
            temperature = float(sys.argv[i+1])
            argumentStart += 2
        elif sys.argv[i] == "--top_k":
            top_k = int(sys.argv[i+1])
            argumentStart += 2
        elif sys.argv[i] == "--top_p":
            top_p = float(sys.argv[i+1])
            argumentStart += 2
        elif sys.argv[i] == "--max_tokens":
            max_tokens = int(sys.argv[i+1])
            argumentStart += 2
        elif (sys.argv[i] == "--output") or (sys.argv[i] == "-o"):
            output_file = sys.argv[i+1]
            argumentStart += 2

# Initialize the Gradio client with the server URL
client = Client(f"http://{ip}:{port}")
# client.view_api()

results = dict()
results["prompt"] = user_prompt

# Open the webcam
cap = cv2.VideoCapture(2)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    sys.exit()

frame_count = 0
try:
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture image from webcam.")
            break

        # Show the frame on the screen
        cv2.imshow('Webcam', frame)

        # Press 'q' to break the loop and stop capturing
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if not is_process_running("festival"):

          # Save the frame to a temporary file
          with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img_file:
            temp_filename = temp_img_file.name
            cv2.imwrite(temp_filename, frame)

          print(f"Performing inference for frame {frame_count}")
          # Send the image and prompt to the Gradio app for processing
          result = client.predict(
            image=handle_file(temp_filename),  # Provide the image file path
            user_prompt=user_prompt,  # The user prompt
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            max_tokens=max_tokens,
            history=[],
            api_name="/predict"
          )

          question = result[0][0]
          response = result[0][1]

          # Printout on screen
          frame_count += 1
          print(f"Processing frame {frame_count}")
          print("Response:", response)

          response.replace('\"','')
          os.system("echo \"%s\" | festival --tts&" % response)
     

          # Store the result in the dictionary
          results[f"frame_{frame_count}"] = response


except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    # Release the webcam and close any open windows
    cap.release()
    cv2.destroyAllWindows()

    # Store the results in a JSON file
    print(f"Storing results in JSON file {output_file}")
    with open(output_file, "w") as outfile:
        json.dump(results, outfile)

