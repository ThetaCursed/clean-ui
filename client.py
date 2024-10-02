from gradio_client import Client, handle_file
#python3 -m pip install gradio_client


# Replace with the actual server URL if different
ip="139.91.90.47"
port="8080"

# Initialize the Gradio client with the server URL
client = Client("http://%s:%s"%(ip,port))  

#client.view_api() 

# Path to your image
image_path = "000000006954.jpg"  # Replace with your image path (This can also be from web)

# Define the user prompt (caption)
user_prompt = "Thoroughly and carefully describe this image."

# Send the image file path and the prompt to the Gradio app for processing
result = client.predict(
    image=handle_file(image_path),   # Provide the file path directly
    user_prompt=user_prompt,  # The user prompt
		temperature=0.6,
		top_k=50,
		top_p=0.9,
		max_tokens=100,
		history=[],
		api_name="/predict"
)

# Output the result
question = result[0][0]
response = result[0][1]

#Printout
print("Response:", result[0][1])

# Save the response to a text file
with open("response.txt", "w") as file:
    file.write(response)
