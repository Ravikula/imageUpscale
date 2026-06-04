================================================
  IMAGE UPSCALER FOR PRINT / BILLBOARD OUTPUT
================================================

Upscales any image (JPG, PNG, etc.) to a target physical print size
and exports it as a print-ready PDF or high-resolution image.


------------------------------------------------
REQUIREMENTS
------------------------------------------------

- Python 3.8 or higher
- The following Python packages:
    Pillow
    reportlab
    opencv-python-headless


------------------------------------------------
INSTALLING PYTHON
------------------------------------------------

macOS:
  1. Install Homebrew (if not already installed):
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

  2. Install Python:
     brew install python

  3. Verify:
     python3 --version

Windows:
  1. Download the installer from https://www.python.org/downloads/
  2. Run the installer — check "Add Python to PATH" before installing
  3. Verify in Command Prompt:
     python --version

Linux (Ubuntu/Debian):
  sudo apt update
  sudo apt install python3 python3-pip


------------------------------------------------
INSTALLING DEPENDENCIES
------------------------------------------------

(Recommended) Create a virtual environment first:

  macOS / Linux:
    python3 -m venv upscaler-env
    source upscaler-env/bin/activate

  Windows:
    python -m venv upscaler-env
    upscaler-env\Scripts\activate

Then install the required packages:

  macOS / Linux:
    pip3 install Pillow reportlab opencv-python-headless

  Windows:
    pip install Pillow reportlab opencv-python-headless

Verify everything installed correctly:

  python3 -c "import PIL; import reportlab; import cv2; print('All good!')"


------------------------------------------------
USAGE
------------------------------------------------

  python3 image_upscaler.py <input_image> --width <W> --height <H> --unit <unit> [options]

Required arguments:
  input             Path to your input image
  --width           Target print width (number)
  --height          Target print height (number)
  --unit            Unit of measurement: in, ft, cm, mm, m

Optional arguments:
  --dpi             Print resolution (default: 150)
                      150 DPI  — billboards and large format banners
                      300 DPI  — posters and close-up print
  --format          Output format: pdf, jpg, png, tiff (default: pdf)
  --output          Custom output file path (default: auto-named)
  --sharpen         Sharpening strength after upscale (default: 1.5)
                      1.0 = no sharpening
                      1.5 = moderate (recommended)
                      2.0 = strong (good for text-heavy images)
  --quality         JPEG output quality 1-100 (default: 95)


------------------------------------------------
EXAMPLES
------------------------------------------------

Billboard (3ft x 2ft) as PDF:
  python3 image_upscaler.py banner.jpg --width 3 --height 2 --unit ft --dpi 150

A4 poster at 300 DPI as PNG:
  python3 image_upscaler.py photo.png --width 21 --height 29.7 --unit cm --dpi 300 --format png

Large banner (90cm x 60cm) as JPEG:
  python3 image_upscaler.py ad.jpg --width 90 --height 60 --unit cm --dpi 100 --format jpg

Custom output filename:
  python3 image_upscaler.py logo.jpg --width 24 --height 16 --unit in --dpi 150 --output my_banner.pdf

Strong sharpening for text-heavy images:
  python3 image_upscaler.py flyer.jpg --width 3 --height 2 --unit ft --sharpen 2.0


------------------------------------------------
SUPPORTED INPUT FORMATS
------------------------------------------------

  .jpg  .jpeg  .png  .bmp  .tiff  .tif  .webp


------------------------------------------------
TIPS FOR BEST RESULTS
------------------------------------------------

- For billboards viewed from a distance, 100-150 DPI is sufficient.
  Going higher just increases file size with no visible improvement.

- For posters or prints viewed up close (within arm's reach), use 300 DPI.

- Use --sharpen 2.0 if your image contains a lot of text or fine lines.

- PDF output is recommended when sending files to a print shop, as it
  embeds the exact physical dimensions (no guessing for the printer).

- TIFF output is preferred by many professional print shops as an
  alternative to PDF.


------------------------------------------------
TROUBLESHOOTING
------------------------------------------------

"pip not found"
  → Try pip3 instead of pip

"python not found"
  → Try python3 instead of python

"ModuleNotFoundError"
  → Re-run the pip install command and check for errors

Permission error on Windows
  → Run Command Prompt as Administrator

Output looks blurry
  → Try increasing --dpi or --sharpen strength

File size is very large
  → Lower --dpi (e.g. 100 for billboards) or use --format jpg with --quality 85


------------------------------------------------
FILES
------------------------------------------------

  image_upscaler.py   — The main script
  README.txt          — This file
