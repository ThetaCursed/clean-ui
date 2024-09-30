import gradio as gr
import torch
import os
from PIL import Image
from transformers import MllamaForConditionalGeneration, AutoModelForCausalLM, AutoProcessor, GenerationConfig

# Set memory management for PyTorch
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'  # or adjust size as needed

# Model selection menu in terminal
print("Select a model to load:")
print("1. Llama-3.2-11B-Vision-Instruct-bnb-4bit")
print("2. Molmo-7B-D-bnb-4bit")
model_choice = input("Enter the number of the model you want to use: ")

if model_choice == "1":
    model_id = "unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit"
    model = MllamaForConditionalGeneration.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    processor = AutoProcessor.from_pretrained(model_id)

elif model_choice == "2":
    model_id = "cyan2k/molmo-7B-D-bnb-4bit"
    arguments = {"device_map": "auto", "torch_dtype": "auto", "trust_remote_code": True}
    model = AutoModelForCausalLM.from_pretrained(model_id, **arguments)
    processor = AutoProcessor.from_pretrained(model_id, **arguments)

else:
    raise ValueError("Invalid model choice. Please enter 1 or 2.")

# Visual theme
visual_theme = gr.themes.Default()  # Default, Soft or Monochrome

# Constants
MAX_OUTPUT_TOKENS = 2048
MAX_IMAGE_SIZE = (1120, 1120)

# Function to process the image and generate a description
def describe_image(image, user_prompt, temperature, top_k, top_p, max_tokens, history):
    # Resize image if necessary
    image = image.resize(MAX_IMAGE_SIZE)

    # Prepare prompt with user input based on selected model
    if model_choice == "1":  # Llama Model
        prompt = f"<|image|><|begin_of_text|>{user_prompt} Answer:"
        # Preprocess the image and prompt
        inputs = processor(image, prompt, return_tensors="pt").to(model.device)

        # Ensure the prompt is not repeated in the output
        if cleaned_output.startswith(user_prompt):
            cleaned_output = cleaned_output[len(user_prompt):].strip()
        
        # Generate output with model
        output = model.generate(
            **inputs,
            max_new_tokens=min(max_tokens, MAX_OUTPUT_TOKENS),
            temperature=temperature,
            top_k=top_k,
            top_p=top_p
        )

        # Decode the raw output
        raw_output = processor.decode(output[0])
        
        # Clean up the output to remove system tokens
        cleaned_output = raw_output.replace("<|image|><|begin_of_text|>", "").strip().replace(" Answer:", "")

    elif model_choice == "2":  # Molmo Model
        # Prepare inputs for Molmo model
        inputs = processor.process(images=[image], text=user_prompt)
        inputs = {k: v.to(model.device).unsqueeze(0) for k, v in inputs.items()}
        
        # Generate output with model, applying the parameters for temperature, top_k, top_p, and max_tokens
        output = model.generate_from_batch(
            inputs,
            GenerationConfig(
                max_new_tokens=min(max_tokens, MAX_OUTPUT_TOKENS),
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                stop_strings="<|endoftext|>",
                do_sample=True
            ),
            tokenizer=processor.tokenizer,
        )

        # Extract generated tokens and decode them to text
        generated_tokens = output[0, inputs["input_ids"].size(1):]
        cleaned_output = processor.tokenizer.decode(generated_tokens, skip_special_tokens=True)

    # Append the new conversation to the history
    history.append((user_prompt, cleaned_output))

    return history

# Function to clear the chat history
def clear_chat():
    return []

# Gradio Interface
def gradio_interface():
    with gr.Blocks(visual_theme) as demo:
        gr.HTML(
        """
    <h1 style='text-align: center'>
    Clean-UI
    </h1>
    """)
        with gr.Row():
            # Left column with image and parameter inputs
            with gr.Column(scale=1):
                image_input = gr.Image(
                    label="Image", 
                    type="pil", 
                    image_mode="RGB", 
                    height=512,  # Set the height
                    width=512   # Set the width
                )

                # Parameter sliders
                temperature = gr.Slider(
                    label="Temperature", minimum=0.1, maximum=2.0, value=0.6, step=0.1, interactive=True)
                top_k = gr.Slider(
                    label="Top-k", minimum=1, maximum=100, value=50, step=1, interactive=True)
                top_p = gr.Slider(
                    label="Top-p", minimum=0.1, maximum=1.0, value=0.9, step=0.1, interactive=True)
                max_tokens = gr.Slider(
                    label="Max Tokens", minimum=50, maximum=MAX_OUTPUT_TOKENS, value=100, step=50, interactive=True)

            # Right column with the chat interface
            with gr.Column(scale=2):
                chat_history = gr.Chatbot(label="Chat", height=512)

                # User input box for prompt
                user_prompt = gr.Textbox(
                    show_label=False,
                    container=False,
                    placeholder="Enter your prompt", 
                    lines=2
                )

                # Generate and Clear buttons
                with gr.Row():
                    generate_button = gr.Button("Generate")
                    clear_button = gr.Button("Clear")

                # Define the action for the generate button
                generate_button.click(
                    fn=describe_image, 
                    inputs=[image_input, user_prompt, temperature, top_k, top_p, max_tokens, chat_history],
                    outputs=[chat_history]
                )

                # Define the action for the clear button
                clear_button.click(
                    fn=clear_chat,
                    inputs=[],
                    outputs=[chat_history]
                )

    return demo

# Launch the interface
demo = gradio_interface()
demo.launch()
