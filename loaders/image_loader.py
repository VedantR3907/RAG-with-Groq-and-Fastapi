import os
import sys
import asyncio
import PIL.Image
import google.generativeai as genai
sys.path.append('../')
from constants.constants import GEMINI_API_KEY
from constants.prompts import IMAGE_DESCRIPTION_PROMPT

# Configure the Generative AI model
genai.configure(api_key=GEMINI_API_KEY)

async def generate_descriptions_for_images(input_directory, output_directory):
    # Supported image extensions
    supported_extensions = ('.jpg', '.jpeg', '.png')

    # List to hold image files and their paths
    image_files = []
    image_paths = []

    # Loop through the directory and filter image files
    for file_name in os.listdir(input_directory):
        if file_name.lower().endswith(supported_extensions):
            image_path = os.path.join(input_directory, file_name)
            image = PIL.Image.open(image_path)
            image_files.append(image)
            image_paths.append(image_path)

    if not image_files:
        print("No images found in the directory.")
        return

    # Initialize the Generative AI model
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")

    # Define the prompt
    prompt = IMAGE_DESCRIPTION_PROMPT

    try:
        # Generate descriptions for all images at once
        response = model.generate_content([prompt] + image_files)

        print(response)

        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)

        # Extract the full description text
        full_description_text = response.candidates[0].content.parts[0].text

        # Split the description text by numbered items (e.g., "1.", "2.", etc.)
        descriptions = []
        current_description = []
        in_description = False

        # Split text into lines and process
        for line in full_description_text.splitlines():
            if line.strip().startswith(tuple(str(i) + '.' for i in range(1, 10))):  # Check if the line starts with a number followed by a dot
                if in_description:
                    descriptions.append('\n'.join(current_description).strip())
                    current_description = []
                in_description = True
            if in_description:
                current_description.append(line)

        if in_description:  # Append the last description
            descriptions.append('\n'.join(current_description).strip())

        # Check if the number of descriptions matches the number of images
        if len(descriptions) != len(image_files):
            print("Warning: The number of descriptions does not match the number of images.")

        # Save each description to a corresponding text file in the output directory
        for i, image_path in enumerate(image_paths):
            if i >= len(descriptions):
                print(f"Warning: No description available for image {os.path.basename(image_path)}")
                continue

            # Get the base name of the image without the extension
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            description = descriptions[i]
            output_file_path = os.path.join(output_directory, f"{image_name}.txt")

            with open(output_file_path, "w") as text_file:
                text_file.write(description)

            print(f"Description saved to {output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage of the async function
async def main():
    input_directory = '../documents'
    output_directory = '../extracted_output'
    await generate_descriptions_for_images(input_directory, output_directory)