import tkinter as tk
from tkinter.colorchooser import askcolor
import tkinter.ttk as ttk
from tkinter import filedialog
from PIL import ImageTk, Image
from cv_handler import Watermarker

FONT = ('Verdana', 12)

        # TODO: Add RGB Selector (or color list with predefined RGB values?) [x]
        # TODO: Add an option for text to stripe across the entire image.    [ ]
        # TODO: Add a checkbox to populate all 9 positions with watermark.   [ ]

class Root(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Image Watermarker, cuz who rly wants to buy Photoshop?')
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        # Initialize attributes
        self.img = None
        self.img_array = None
        self.pil_img = None
        self.logo = None
        self.logo_filepath = None
        self.img_filepath = None
        self.screen_width = int(self.winfo_screenwidth() * 0.5)  # cuz 2 monitors
        self.screen_height = self.winfo_screenheight()
        self.resizable = True

        # Image Upload
        self.img_upload_label = tk.Label(self, text='Upload an image:', font=FONT, anchor='e')
        self.img_upload_label.grid(column=0, row=0, padx=10, pady=10, sticky='ew')
        self.img_upload_button = ttk.Button(self, text='Open Image', command=self.upload_pic)
        self.img_upload_button.grid(column=1, row=0, padx=20, pady=10, sticky='ew')

        # Logo Upload
        self.logo_upload_label = tk.Label(self, text='Upload a logo:', font=FONT, anchor='e')
        self.logo_upload_label.grid(column=0, row=1, padx=10, pady=10, sticky='ew')
        self.logo_upload_button = ttk.Button(self, text='Add Logo', command=self.upload_logo)
        self.logo_upload_button.grid(column=1, row=1, padx=20, pady=10, sticky='ew')
        self.logo_upload_button['state'] = 'disabled'

        # Watermark Text
        self.watermark_text_frame = tk.Frame(self, height=200)
        self.watermark_text_frame.grid(column=0, row=2, columnspan=2, rowspan=4,)
        self.watermark_text_label = tk.Label(self.watermark_text_frame, text='Use text:', font=FONT, anchor='e')
        self.watermark_text_label.grid(column=0, row=0, sticky='ew', padx=20)

        self.text = tk.StringVar()
        self.watermark_text = ttk.Entry(self.watermark_text_frame, textvariable=self.text)
        self.watermark_text.grid(column=1, row=0, padx=20, pady=10, sticky='ew')

        # Text Size Slider
        self.text_size_label = tk.Label(self.watermark_text_frame, text='Text Size:', font=FONT, anchor='e')
        self.text_size_label.grid(column=0, row=1, sticky='ew', padx=20, pady=10)
        self.text_size_slider = ttk.Scale(self.watermark_text_frame, from_=0.5, to=4, orient='horizontal')
        self.text_size_slider.grid(column=1, row=1, sticky='ew', padx=20, pady=10)

        # Text Thickness Slider
        self.text_thickness_label = tk.Label(self.watermark_text_frame, text='Text Thickness:', font=FONT, anchor='e')
        self.text_thickness_label.grid(column=0, row=2, sticky='ew', padx=20, pady=10)
        self.text_thickness_slider = ttk.Scale(self.watermark_text_frame, from_=0.0, to=10, orient='horizontal')
        self.text_thickness_slider.grid(column=1, row=2, sticky='ew', padx=20, pady=10)

        # Opacity Slider
        self.overlay_label = tk.Label(self.watermark_text_frame, text='Watermark Opacity:', font=FONT, anchor='e')
        self.overlay_label.grid(column=0, row=3, padx=20, pady=10, sticky='ew')
        self.overlay_slider = ttk.Scale(self.watermark_text_frame, from_=0.0, to=100, orient='horizontal', command=self.update_image)
        self.overlay_slider.grid(column=1, row=3, padx=20, pady=10, sticky='ew')

        # Font Options
        self.font_choice_frame = tk.Frame(self)
        self.font_choice_frame.grid(column=0, row=6, columnspan=2, rowspan=2, sticky='ew', pady=10)
        self.font_choice_label = tk.Label(self.font_choice_frame, text='Font Type:', font=FONT, anchor='e')
        self.font_choice_label.grid(column=0, row=0, padx=20, sticky='ew')
        self.font_choice = tk.StringVar()
        self.font_choices = ttk.Combobox(self.font_choice_frame, textvariable=self.font_choice)
        self.font_choices['values'] = ('Sans Serif', 'Serif', 'Cursive')
        self.font_choices['state'] = 'readonly'
        self.font_choices.set('Sans Serif')
        self.font_choice.set('Sans Serif')
        self.font_choices.grid(column=1, row=0, padx=20, pady=10, sticky='ew')
        self.font_color_label = tk.Label(self.font_choice_frame, text='Change Text Color:', font=FONT, anchor='e')
        self.font_color_label.grid(column=0, row=1, padx=20, sticky='ew')
        self.font_color_button = ttk.Button(self.font_choice_frame, text='Choose Color', command=self.set_font_color)
        self.font_color_button.grid(column=1, row=1, padx=20, sticky='ew')
        self.font_color = (255, 255, 255)

        # Watermark Position Selection
        self.logo_position = tk.StringVar()
        self.radio_frame = tk.Frame(self)
        self.radio_frame.grid(column=0, row=8, columnspan=2, pady=10)
        self.radio_label = tk.Label(self.radio_frame, text='Select Watermark Position')
        self.radio_label.grid(column=0, row=0, padx=20, sticky='ew', columnspan=3)

        self.top_left_radio = tk.Radiobutton(self.radio_frame, text='Top Left', value='top_left',
                                             variable=self.logo_position, command=self.update_image)
        self.left_radio = tk.Radiobutton(self.radio_frame, text='Left', value='left', variable=self.logo_position, command=self.update_image)
        self.bottom_left_radio = tk.Radiobutton(self.radio_frame, text='Bottom Left', value='bottom_left',
                                                variable=self.logo_position, command=self.update_image)
        self.top_left_radio.grid(column=0, row=1, sticky='w', padx=10)
        self.left_radio.grid(column=0, row=2, sticky='w', padx=10)
        self.bottom_left_radio.grid(column=0, row=3, sticky='w', padx=10)

        self.center_top_radio = tk.Radiobutton(self.radio_frame, text='Top', value='top_center',
                                               variable=self.logo_position, command=self.update_image)
        self.center_radio = tk.Radiobutton(self.radio_frame, text='Center', value='center', variable=self.logo_position, command=self.update_image)
        self.center_bottom_radio = tk.Radiobutton(self.radio_frame, text='Bottom', value='bottom_center',
                                                  variable=self.logo_position, command=self.update_image)
        self.center_top_radio.grid(column=1, row=1, sticky='w', padx=20)
        self.center_radio.grid(column=1, row=2, sticky='w', padx=20)
        self.center_bottom_radio.grid(column=1, row=3, sticky='w', padx=20)

        self.top_right_radio = tk.Radiobutton(self.radio_frame, text='Top Right', value='top_right',
                                              variable=self.logo_position, command=self.update_image)
        self.right_radio = tk.Radiobutton(self.radio_frame, text='Right', value='right', variable=self.logo_position, command=self.update_image)
        self.bottom_right_radio = tk.Radiobutton(self.radio_frame, text='Bottom Right', value='bottom_right',
                                                 variable=self.logo_position, command=self.update_image)
        self.top_right_radio.grid(column=2, row=1, sticky='w')
        self.right_radio.grid(column=2, row=2, sticky='w')
        self.bottom_right_radio.grid(column=2, row=3, sticky='w')
        self.center_radio.select()

        self.confirm_button = ttk.Button(self, text='Confirm', command=self.update_image)
        self.confirm_button.grid(column=1, row=9, padx=20, pady=10, sticky='ew')
        self.confirm_button['state'] = 'disabled'
        self.save_button = ttk.Button(self, text=' Save ', command=self.save_pic)
        self.save_button.grid(column=0, row=9, padx=20, pady=10, sticky='ew')
        self.save_button['state'] = 'disabled'

        self.canvas = tk.Canvas(self, width=1080, height=800, borderwidth=1, bg='grey')
        self.canvas.grid(column=2, row=0, rowspan=10, padx=9, pady=10)
        self.watermarker = Watermarker(screen_width=self.screen_width, screen_height=self.screen_height)

    def upload_pic(self):
        self.img_filepath = filedialog.askopenfilename()
        # Catch if user hits Cancel
        self.img_filepath = None if self.img_filepath == '' else self.img_filepath
        if self.img_filepath is None:
            return
        self.watermarker.upload_img(image_path=self.img_filepath, screen_width=self.screen_width,
                                    screen_height=self.screen_height)
        self.logo_upload_button['state'] = 'active'
        self.img_array = self.watermarker.get_img_array()
        self.pil_img = Image.fromarray(self.img_array)
        self.img = ImageTk.PhotoImage(self.pil_img)
        self.canvas.config(height=self.img.height(), width=self.img.width())
        self.canvas_image = self.canvas.create_image((0, 0), image=self.img, anchor=tk.NW)
        self.enable_buttons()

    def upload_logo(self):
        self.logo_filepath = filedialog.askopenfilename()
        # Catch if user hits Cancel
        self.logo_filepath = None if self.logo_filepath == '' else self.logo_filepath
        if self.logo_filepath is not None:
            self.watermarker.upload_logo(logo_path=self.logo_filepath)
            self.logo = ImageTk.PhotoImage(Image.fromarray(self.watermarker.get_logo_array()))
            self.watermark = self.canvas.create_image(
                (int(self.img.width() / 2), int(self.img.height() / 2)), image=self.logo)
            self.enable_buttons()

    def update_image(self, *args):
        txt = None if self.text.get() == '' else self.text.get()
        print(f'Text fetched: {txt}')
        self.watermarker.refresh_array()
        if self.logo is not None:
            position_fn = self.watermarker.pos_fns[self.logo_position.get()]
            position_fn()
        if self.img is not None:
            txt_pos = self.watermarker.get_txt_pos(self.logo_position.get())
            text_size = self.text_size_slider.get()
            font = self.font_choice.get()
            text_thickness = self.text_thickness_slider.get()
            print(f'text size: {text_size}')
            self.img_array = self.watermarker.add_watermark(opacity=self.overlay_slider.get()/100, text=txt, pos=txt_pos,
                                                            text_size=text_size, text_thickness=text_thickness, font=font, 
                                                            font_color=self.font_color)
            self.pil_img = Image.fromarray(self.img_array)
            self.display_new_img(self.pil_img)

    def set_font_color(self):
        self.font_color = askcolor(title='Font Color')[0]
        print(self.font_color)
        self.font_color = (255, 255, 255) if self.font_color is None \
            else (self.font_color[2], self.font_color[1], self.font_color[0])
        self.update_image()

    def enable_buttons(self):
        self.confirm_button['state'] = 'active'
        self.save_button['state'] = 'active'

    def change_size(self):
        pass

    def display_new_img(self, new_img):
        self.img = ImageTk.PhotoImage(new_img)
        self.canvas.config(height=self.img.height(), width=self.img.width())
        self.canvas_image = self.canvas.create_image((0, 0), image=self.img, anchor='nw')

    def save_pic(self):
        """Saves pic from original (not resized, as with the display)"""
        loc = filedialog.asksaveasfile()
        if loc == '':
            return  # Catch if user clicks Cancel
        txt = None if self.text.get() == '' else self.text.get()
        print(f'Text fetched: {txt}')
        if self.logo is not None:
            self.watermarker.format_original_for_writing()
            position_fn = self.watermarker.pos_fns[self.logo_position.get()]
            position_fn(original=True)
        txt_pos = self.watermarker.get_txt_pos(self.logo_position.get(), original=True)
        text_size = self.text_size_slider.get()
        text_thickness = self.text_thickness_slider.get()
        font = self.font_choice.get()
        print(f'text size: {text_size}')
        self.img_array = self.watermarker.watermark_original_for_writing(opacity=self.overlay_slider.get()/100,
                                                                         text=txt, pos=txt_pos,
                                                                         text_size=text_size,
                                                                         text_thickness=text_thickness,
                                                                         font=font)
        self.pil_img = Image.fromarray(self.img_array)
        self.pil_img.save(loc)

