# Image Watermarker
## For those of us who don't want to pay for a fancy image editor.

![Watermarked Image](https://github.com/Kolkhis/image_watermarker/assets/36500473/1382e4d0-f4dd-4f31-8587-e1205e6d07b9)
> *Image watermarked with a wall titan in my PC.*

May look different on your PC. Application theme follows your system theme.

To use, navigate to the project directory and run: 
`pip install -r requirements.txt`

## Features
* Uses `opencv-python` to manipulate images.
    * If you didn't install from `requirements.txt`: `pip install opencv-python`
* Uses `customtkinter` for some nice visuals. 
    * * If you didn't install from `requirements.txt`: `pip install customtkinter`
    * This can be changed in `main.py` if you prefer to use Python's standard `tkinter`.
* Add text watermark to image with any given size, color, and opacity.
* Add an image watermark (logo) at any given opacity.
* Images resize to fit in the GUI, but are saved as their original size.

### Using Tkinter instead of CustomTkinter:
Uncomment the import from `app.py` and comment the import from `custom_gui.py`:
> ![Use Tkinter Instead of CustomTkinter](https://github.com/Kolkhis/image_watermarker/assets/36500473/42f20e90-b1f3-4060-b2c0-1b8427ff2434)

### Font Colors
Choose any font color you want for the watermark text.
![Font Colors Demo](https://github.com/Kolkhis/image_watermarker/assets/36500473/d311b22b-69ea-4f16-a65d-3f003f0a779f)


## Features to be Added
* Add option to watermark multiple parts of an image at the same time.

Feedback and suggestions are appreciated!

