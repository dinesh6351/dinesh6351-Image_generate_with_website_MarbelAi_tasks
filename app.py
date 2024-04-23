from flask import Flask, render_template, request
import os
from rembg import remove
from PIL import Image

app = Flask(__name__, static_folder='output_advertisement')

# Function to remove white background from product images
def remove_background(input_path, output_path):
    with open(input_path, "rb") as f:
        img = remove(f.read())
    with open(output_path, "wb") as f:
        f.write(img)

@app.route('/',methods=['GET', 'POST'])
def home():
     return render_template('index.html')

@app.route('/background', methods=['GET', 'POST'])
def background():
    if request.method == 'POST':
        # Handle file upload
        for i in range(1, 6):  # Iterate from file1 to file5
            file_key = f'file{i}'
            uploaded_file = request.files[file_key]
            
            if uploaded_file.filename != '':
                # Save uploaded file
                input_product_folder = "background_images"
                uploaded_file.save(os.path.join(input_product_folder, uploaded_file.filename))
    return render_template('background.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Handle file upload
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            # Save uploaded file
            input_product_folder = "input_product"
            uploaded_file.save(os.path.join(input_product_folder, uploaded_file.filename))

            # Process uploaded image
            product_image_path = os.path.join(input_product_folder, uploaded_file.filename)
            output_advertisement_folder = "output_advertisement"
            image_paths = remove_and_merge_images(product_image_path, output_advertisement_folder)
            print(image_paths)
            return render_template('upload_success.html', image_paths=image_paths)
    return render_template('upload.html')


def remove_and_merge_images(input_path, output_folder):
    image_paths = []

    # Function to remove white background from product images and merge with different backgrounds
    with open(input_path, "rb") as f:
        img = remove(f.read())

    product_name = os.path.splitext(os.path.basename(input_path))[0]
    product_output_folder = os.path.join(output_folder, product_name)
    os.makedirs(product_output_folder, exist_ok=True)

    with open(os.path.join(product_output_folder, f"no_bg_{product_name}.png"), "wb") as f:
        f.write(img)

    backgrounds_folder = "background_images"
    background_images = [f for f in os.listdir(backgrounds_folder) if os.path.isfile(os.path.join(backgrounds_folder, f))]

    for i, background_image_name in enumerate(background_images):
        background_image_path = os.path.join(backgrounds_folder, background_image_name)
        background = Image.open(background_image_path).convert("RGBA")
        product_no_bg = Image.open(os.path.join(product_output_folder, f"no_bg_{product_name}.png")).convert("RGBA")
        background = background.resize(product_no_bg.size, Image.LANCZOS)
        advertisement_image = Image.alpha_composite(background, product_no_bg)
        output_image_path = os.path.join(product_output_folder, f"{product_name}_bg_{i+1}.png")
        advertisement_image.save(output_image_path)
        image_paths.append(output_image_path)

    return image_paths


if __name__ == '__main__':
    app.run(debug=True)
