import customtkinter as ctk
import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter import filedialog
from PIL import ImageTk, Image
from cv_handler import Watermarker

FONT = ('Verdana', 12)
BG_COLOR = '#454545'

# '#454545'  -  Dark Grey
        # TODO: Add RGB Selector (or color list with predefined RGB values?) [x]
        # TODO: Add an option for text to stripe across the entire image.    [ ]
        # TODO: Add a checkbox to populate all 9 positions with watermark.   [ ]
        # TODO: Add a 'Stack Words' option to add newlines between words:    [ ]

class Root(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Image Watermarker, cuz who rly wants to buy Photoshop?')

        # Initialize attributes
        self.img = None
        self.img_array = None
        self.pil_img = None
        self.logo = None
        self.logo_filepath = None
        self.img_filepath = None
        self.screen_width = int(self.winfo_screenwidth() * 0.5)  # cuz 2 monitors
        self.screen_height = self.winfo_screenheight()

        # Change root color scheme
        self.configure(background=BG_COLOR)

        # Image Upload
        self.img_upload_label = ctk.CTkLabel(self, text='Upload an image:', anchor='e')
        self.img_upload_label.grid(column=0, row=0, padx=10, pady=10, sticky='ew')
        self.img_upload_button = ctk.CTkButton(self, text='Open Image', command=self.upload_pic, border_color='black', border_width=1)
        self.img_upload_button.grid(column=1, row=0, padx=20, pady=10, sticky='ew')

        # Logo Upload
        self.logo_upload_label = ctk.CTkLabel(self, text='Upload a logo:', justify='right', anchor='e')
        self.logo_upload_label.grid(column=0, row=1, padx=10, pady=10, sticky='ew')
        self.logo_upload_button = ctk.CTkButton(self, text='Add Logo', command=self.upload_logo, border_color='black', border_width=1)
        self.logo_upload_button.grid(column=1, row=1, padx=20, pady=10, sticky='ew')
        self.logo_upload_button['state'] = 'disabled'

        # Watermark Text
        self.watermark_text_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.watermark_text_frame.grid(column=0, row=2, columnspan=2, rowspan=5,)
        self.watermark_text_label = ctk.CTkLabel(self.watermark_text_frame, text='Use text:', anchor='e')
        self.watermark_text_label.grid(column=0, row=0, sticky='ew', padx=20)

        self.text = tk.StringVar(master=self)
        self.watermark_text = ctk.CTkEntry(self.watermark_text_frame)
        self.watermark_text.grid(column=1, row=0, padx=20, pady=10, sticky='ew')

        # Text Size Slider
        self.text_size_label = ctk.CTkLabel(self.watermark_text_frame, text='Text Size:', anchor='e')
        self.text_size_label.grid(column=0, row=1, sticky='ew', padx=20, pady=10)
        self.text_size_slider = ctk.CTkSlider(self.watermark_text_frame, from_=1, to=4, command=self.update_image)
        self.text_size_slider.grid(column=1, row=1, sticky='ew', padx=20, pady=10)

        # Text Thickness Slider
        self.text_thickness_label = ctk.CTkLabel(self.watermark_text_frame, text='Text Thickness:', anchor='e')
        self.text_thickness_label.grid(column=0, row=2, sticky='ew', padx=20, pady=10)
        self.text_thickness_slider = ctk.CTkSlider(self.watermark_text_frame, from_=0, to=10, command=self.update_image)
        self.text_thickness_slider.grid(column=1, row=2, sticky='ew', padx=20, pady=10)

        # Opacity Slider
        self.overlay_label = ctk.CTkLabel(self.watermark_text_frame, text='Watermark Opacity:', anchor='e')
        self.overlay_label.grid(column=0, row=3, padx=20, pady=10, sticky='ew')
        self.overlay_slider = ctk.CTkSlider(self.watermark_text_frame, from_=0, to=100, command=self.update_image)
        self.overlay_slider.grid(column=1, row=3, padx=20, pady=10, sticky='ew')

        # Font Options
        self.font_choice_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.font_choice_frame.grid(column=0, row=7, columnspan=2, rowspan=3, sticky='ew', pady=10)
        self.font_choice_label = ctk.CTkLabel(self.font_choice_frame, text='Font Type:', anchor='e')
        self.font_choice_label.grid(column=0, row=0, padx=20, sticky='ew')
        self.font_choices = ctk.CTkComboBox(self.font_choice_frame, values=['Sans Serif 1', 'Sans Serif 2','Sans Serif (small)', 
                                                                            'Serif 1', 'Serif 2', 'Serif (small)',
                                                                            'Cursive 1', 'Cursive 2'])
        self.font_choices['values'] = ('Sans Serif 1', 'Serif 1', 'Cursive 1','Sans Serif 2', 'Sans Serif (small)', 'Serif 2', 'Serif (small)', 'Cursive 2',)
        self.font_choices['state'] = 'readonly'
        self.font_choices.set('Sans Serif 1')
        self.font_choices.grid(column=1, row=0, padx=20, pady=10, sticky='ew')
        self.font_color_label = ctk.CTkLabel(self.font_choice_frame, text='Change Text Color:', anchor='e')
        self.font_color_label.grid(column=0, row=1, padx=20, sticky='ew')
        self.font_color_button = ctk.CTkButton(self.font_choice_frame, text='Choose Color', command=self.set_font_color, border_color='black', border_width=1)
        self.font_color_button.grid(column=1, row=1, padx=20, sticky='ew')
        self.font_color = (255, 255, 255)

        # Watermark Position Selection
        self.logo_position = tk.StringVar(master=self)
        self.logo_position.set('center')
        self.radio_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.radio_frame.grid(column=0, row=10, columnspan=2, pady=10)
        self.radio_label = ctk.CTkLabel(self.radio_frame, text='Select Watermark Position', anchor='center')
        self.radio_label.grid(column=0, row=0, padx=20, sticky='ew', columnspan=3)

        self.top_left_radio = ctk.CTkRadioButton(master=self.radio_frame, hover=True, text='Top Left', value='top_left',
                                                 variable=self.logo_position, command=self.update_image,)
        self.left_radio = ctk.CTkRadioButton(master=self.radio_frame, hover=True, text='Left', value='left',
                                             variable=self.logo_position, command=self.update_image,)
        self.bottom_left_radio = ctk.CTkRadioButton(master=self.radio_frame, hover=True, text='Bottom Left', value='bottom_left',
                                                    variable=self.logo_position, command=self.update_image,)
        self.top_left_radio.grid(column=0, row=1, sticky='w', padx=10, pady=10)
        self.left_radio.grid(column=0, row=2, sticky='w', padx=10, pady=10)
        self.bottom_left_radio.grid(column=0, row=3, sticky='w', padx=10, pady=10)

        self.center_top_radio = ctk.CTkRadioButton(master=self.radio_frame, hover=True, text='Top',
                                                   value='top_center', variable=self.logo_position,
                                                   command=self.update_image,)
        self.center_radio = ctk.CTkRadioButton(master=self.radio_frame, hover=True, text='Center', value='center',
                                               variable=self.logo_position, command=self.update_image,)
        self.center_bottom_radio = ctk.CTkRadioButton(master=self.radio_frame, hover=True, text='Bottom', value='bottom_center',
                                                      variable=self.logo_position, command=self.update_image,)
        self.center_top_radio.grid(column=1, row=1, sticky='w', padx=20, pady=10)
        self.center_radio.grid(column=1, row=2, sticky='w', padx=20, pady=10)
        self.center_bottom_radio.grid(column=1, row=3, sticky='w', padx=20, pady=10)

        self.top_right_radio = ctk.CTkRadioButton(master=self.radio_frame, hover=True, text='Top Right', value='top_right',
                                                  variable=self.logo_position, command=self.update_image,)
        self.right_radio = ctk.CTkRadioButton(master=self.radio_frame, hover=True, text='Right', value='right',
                                              variable=self.logo_position, command=self.update_image,)
        self.bottom_right_radio = ctk.CTkRadioButton(master=self.radio_frame, hover=True, text='Bottom Right', value='bottom_right',
                                                     variable=self.logo_position, command=self.update_image,)
        self.top_right_radio.grid(column=2, row=1, sticky='w', pady=10)
        self.right_radio.grid(column=2, row=2, sticky='w', pady=10)
        self.bottom_right_radio.grid(column=2, row=3, sticky='w', pady=10)
        self.center_radio.select()

        self.confirm_button = ctk.CTkButton(self, text='Confirm', command=self.update_image, border_color='black', border_width=1)
        self.confirm_button.grid(column=1, row=11, padx=20, pady=10, sticky='ew')
        self.confirm_button['state'] = 'disabled'
        self.save_button = ctk.CTkButton(self, text=' Save ', command=self.save_pic, border_color='black', border_width=1)
        self.save_button.grid(column=0, row=11, padx=20, pady=10, sticky='ew')
        self.save_button['state'] = 'disabled'

        self.canvas = tk.Canvas(self, width=1000, height=750, borderwidth=1, highlightthickness=0)
        self.canvas.grid(column=2, row=0, rowspan=12, padx=9, pady=10)
        self.watermarker = Watermarker(screen_width=int(self.canvas.winfo_width()),
                                       screen_height=int(self.canvas.winfo_height()),
                                       max_screen_height=self.screen_height)

    def upload_pic(self):
        self.img_filepath = filedialog.askopenfilename()
        self.initial_filename = self.img_filepath.split('/')[-1]
        # Catch if user hits Cancel
        self.img_filepath = None if self.img_filepath == '' else self.img_filepath
        if self.img_filepath is None:
            return
        self.watermarker.upload_img(image_path=self.img_filepath, screen_width=self.screen_width,
                                    screen_height=self.screen_height)
        self.logo_upload_button['state'] = 'active'
        self.watermarker.refresh_array()
        self.img_array = self.watermarker.get_img_array()
        self.pil_img = Image.fromarray(self.img_array)
        self.img = ImageTk.PhotoImage(self.pil_img)
        self.enable_buttons()
        self.update_image()
        self.after(150, self.update_image)


    def upload_logo(self):
        self.logo_filepath = filedialog.askopenfilename()
        # Catch if user hits Cancel
        self.logo_filepath = None if self.logo_filepath == '' else self.logo_filepath
        if self.logo_filepath is not None:
            self.watermarker.upload_logo(logo_path=self.logo_filepath)
            self.logo = ImageTk.PhotoImage(Image.fromarray(self.watermarker.get_logo_array()))
            self.watermark = self.canvas.create_image( (int(self.img.width() / 2), int(self.img.height() / 2)), image=self.logo)
            self.enable_buttons()

    def update_image(self, *args):
        txt = None if self.watermark_text.get() == '' else self.watermark_text.get()
        self.watermarker.refresh_array()
        if self.logo is not None:
            position_fn = self.watermarker.pos_fns[self.logo_position.get()]
            position_fn()
        if self.img is not None:
            txt_pos = self.watermarker.get_txt_pos(self.logo_position.get())
            text_size = self.text_size_slider.get()
            font = self.font_choices.get()
            text_thickness = self.text_thickness_slider.get()
            self.img_array = \
            self.watermarker.add_watermark(opacity=self.overlay_slider.get()/100,
                                           text=txt, pos=txt_pos,
                                           text_size=text_size,
                                           text_thickness=text_thickness,
                                           font=font,
                                           font_color=self.font_color)
            self.pil_img = Image.fromarray(self.img_array)
            self.display_new_img(self.pil_img)

    def set_font_color(self):
        self.font_color = askcolor(title='Font Color')[0]
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
        placement = (int(self.canvas.winfo_width() * 0.5), int(self.canvas.winfo_height() * 0.5))
        self.canvas_image = self.canvas.create_image(placement, image=self.img)

    def save_pic(self):
        """Saves pic from original (not resized, as with the display)"""
        file_type = self.initial_filename.split(".")[-1]
        file_name = f'watermarked_{self.initial_filename}'
        types = [( f'.{file_type}' , f'*.{file_type}'), ('All Files', '*.*')]
        loc = filedialog.asksaveasfile(filetypes=types, defaultextension=types[0], initialfile=file_name)
        if loc == '':
            return  # Catch if user clicks Cancel
        txt = None if self.watermark_text.get() == '' else self.watermark_text.get()
        if self.logo is not None:
            position_fn = self.watermarker.pos_fns[self.logo_position.get()]
            position_fn(original=True)
        txt_pos = self.watermarker.get_txt_pos(self.logo_position.get(), original=True)
        text_size = self.text_size_slider.get()
        text_thickness = self.text_thickness_slider.get()
        font = self.font_choices.get()
        font_color = self.font_color
        self.watermarker.format_original_for_writing()
        self.img_array = self.watermarker.watermark_original_for_writing(opacity=self.overlay_slider.get()/100,
                                                                         text=txt, pos=txt_pos,
                                                                         text_size=text_size,
                                                                         text_thickness=text_thickness,
                                                                         font=font, font_color=font_color)
        self.pil_img = Image.fromarray(self.img_array)
        self.pil_img.save(loc)

