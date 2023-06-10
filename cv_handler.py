import numpy as np
import cv2


class Watermarker:
    def __init__(self, **kwargs):
        self.logo_resized = False
        self.img_resized = False
        self.screen_height = kwargs.get('screen_height')
        self.screen_width = kwargs.get('screen_width')
        self.fonts = {
                'Sans Serif': cv2.FONT_HERSHEY_DUPLEX,
                'Serif': cv2.FONT_HERSHEY_TRIPLEX,
                'Cursive': cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
                }
        if kwargs.get('img_path'):
            image_path = kwargs.get('img_path')
            self.img = cv2.imread(image_path)
            self.original_img = self.img.copy()
            self.img_height, self.img_width = self.img.shape[:2]
            self.alpha = np.arange(0, 1.1, 0.1)
            self.alpha = self.alpha[-1]
            self.img_filename = image_path.split('/')[-1]
            self.output = self.img.copy()
            self.overlay = self.img.copy()
            self.img_size = self.img.shape[:2]
            self.middle = (int(self.img_size[0] * 0.42), int(self.img_size[1] * 0.5))
        else:
            self.img, self.original_img = None, None
        if kwargs.get('logo_path'):
            self.logo = cv2.imread(kwargs.get('logo_path'))
            self.original_logo = self.logo.copy()
            self.logo_height, self.logo_width = self.logo.shape[:2]
            self.update_dimensions()
            if self.logo_height > self.img_height*0.5:
                self.logo = cv2.resize(self.logo, (int(self.img_height*0.5), int(self.img_width*0.5)))
                self.update_dimensions()
                self.logo_resized = True
            self.center_y = int(self.img_height * 0.5)
            self.center_x = int(self.img_width * 0.5)

            self.top_y = self.center_y - int(self.logo_height * 0.5)
            self.left_x = self.center_x - int(self.logo_width * 0.5)
            self.bottom_y = self.top_y + self.logo_height
            self.right_x = self.left_x + self.logo_width
        else:
            self.logo, self.original_logo = None, None
        self.pos_fns = {'top_right': self.top_right_logo,
                        'top_left': self.top_left_logo,
                        'top_center': self.center_top_logo,
                        'center': self.center_logo,
                        'bottom_right': self.bottom_right_logo,
                        'bottom_left': self.bottom_left_logo,
                        'bottom_center': self.center_bottom_logo,
                        'left': self.left_logo,
                        'right': self.right_logo}

    def update_dimensions(self):
        if self.logo is not None:
            self.logo_height, self.logo_width = self.logo.shape[:2]
        if self.img is not None:
            self.img_height, self.img_width = self.img.shape[:2]

    def calculate_destination(self, **kwargs):
        if kwargs.get('original') and self.original_logo is not None:
            self.original_top_y = self.original_center_y - int(self.original_logo_height * 0.5)
            self.original_left_x = self.original_center_x - int(self.original_logo_width * 0.5)
            self.original_bottom_y = self.original_top_y + self.original_logo_height
            self.original_right_x = self.original_left_x + self.original_logo_width
            self.original_destination = self.original_img[self.original_top_y:self.original_bottom_y, self.original_left_x:self.original_right_x]
            return
        if self.logo is not None:
            self.top_y = self.center_y - int(self.logo_height * 0.5)
            self.left_x = self.center_x - int(self.logo_width * 0.5)
            self.bottom_y = self.top_y + self.logo_height
            self.right_x = self.left_x + self.logo_width
            self.destination = self.img[self.top_y:self.bottom_y, self.left_x:self.right_x]
            self.overlay_destination = self.overlay[self.top_y:self.bottom_y, self.left_x:self.right_x]

    def upload_img(self, image_path, **kwargs):
        """Reads an image into an ndarray to be watermarked by the logo image."""
        self.img = cv2.imread(image_path)
        self.original_img = self.img.copy()
        self.original_height, self.original_width = self.original_img.shape[:2]
        self.alpha = np.arange(0, 1.1, 0.1)
        self.screen_height = kwargs.get('screen_height')
        self.screen_width = kwargs.get('screen_width')
        self.img_size = self.img.shape[:2]
        self.update_dimensions()
        self.alpha = self.alpha[-1]
        if self.screen_height is not None and self.img_height > self.screen_height:
            print(f'Image resizing (height): {self.img.shape[:2]}')
            y = self.screen_height / self.img_height
            self.img = cv2.resize(self.img, (int(self.img_width*y), int(self.img_height*y)))
            self.img_resized = True
            print(f'Image resized (height): {self.img.shape[:2]}')
            self.update_dimensions()
        if self.screen_width is not None and self.img_width > self.screen_width*0.5:
            print(f'Image resizing (width): {self.img.shape[:2]}')
            x = self.screen_width / self.img_width
            self.img = cv2.resize(self.img, (int(self.img_width*x), int(self.img_height*x)))
            self.img_resized = True
            self.update_dimensions()
            print(f'Image resized (width): {self.img.shape[:2]}')
        self.update_dimensions()
        self.original_height, self.original_width = self.img.shape[:2]
        self.img_filename = image_path.split('/')[-1]
        self.output = self.img.copy()
        self.overlay = self.img.copy()
        self.middle = (int(self.img_height*0.42), int(self.img_width*0.5))
        self.working_img = self.img

    def get_img_array(self):
        return cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)

    def get_logo_array(self):
        return cv2.cvtColor(self.logo, cv2.COLOR_BGR2RGB)

    def upload_logo(self, logo_path):
        """Reads an image into an ndarray to watermark the parent image. Returns nothing."""
        self.logo = cv2.imread(logo_path)
        self.original_logo = self.logo.copy()
        self.logo_height, self.logo_width = self.logo.shape[:2]
        self.update_dimensions()
        # Resize logo image if it's too big. Will result in runtime errors otherwise.
        if self.logo_height > self.img_height * 0.5:
            print(f'Logo before resizing (height): {self.logo.shape[:2]}')
            y = (self.img_height * 0.5) / self.logo_height
            self.logo = cv2.resize(self.logo, (int(self.logo_width*y), int(self.logo_height*y)))
            self.logo_resized = True
            print(f'Logo after (height) resizing: {self.logo.shape[:2]}')
            self.update_dimensions()
        if self.logo_width > self.img_width * 0.5:
            print(f'Logo before (width) resizing: {self.logo.shape[:2]}')
            x = (self.img_width * 0.5) / self.logo_width
            self.logo = cv2.resize(self.logo, (int(self.logo_width*x), int(self.logo_height*x)))
            self.logo_resized = True
            print(f'Logo after (width) resizing: {self.logo.shape[:2]}')
            self.update_dimensions()
        self.center_y = int(self.img_height * 0.5)
        self.center_x = int(self.img_width * 0.5)
        self.calculate_destination()
        self.working_logo = self.logo

    def add_watermark(self, opacity, **kwargs):
        """Adds watermark to image. Must call one of the positioning functions first!
        Returns:
            ndarray representing image"""
        self.refresh_array()
        self.overlay = self.working_img.copy()
        if kwargs.get('text') is not None:
            pos = (kwargs.get('pos'))
            text_size = int(kwargs.get('text_size', 1))
            text_thickness = int(kwargs.get('text_thickness', 1))
            font_color = kwargs.get('font_color', (255, 255, 255))
            font_choice = self.fonts[kwargs.get('font')]
            cv2.putText(self.overlay, kwargs.get('text'), pos, font_choice, text_size, font_color, text_thickness, cv2.LINE_AA)
            self.img = cv2.addWeighted(self.img, 1 - opacity, self.overlay, opacity, 0.0)
        if self.logo is not None and self.img is not None:
            self.calculate_destination()
            watermarked_area = cv2.addWeighted(self.destination, 1.0, self.logo, opacity, 0.0)
            self.img[self.top_y:self.bottom_y, self.left_x:self.right_x] = watermarked_area
            return cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        return cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)

    def watermark_original_for_writing(self, opacity, **kwargs):
        if kwargs.get('text') is not None:
            pos = (kwargs.get('pos'))
            text_size = int(kwargs.get('text_size'))
            font_choice = self.fonts[kwargs.get('font')]
            text_thickness = int(kwargs.get('text_thickness'))
            font_color = kwargs.get('font_color')
            self.original_overlay = self.original_img.copy()
            cv2.putText(self.original_overlay, kwargs.get('text'), pos, font_choice, text_size, font_color, text_thickness, cv2.LINE_AA)
            self.original_img = cv2.addWeighted(self.original_img, 1 - opacity, self.original_overlay, opacity, 0.0)
        if self.original_logo is not None and self.original_img is not None:
            self.calculate_destination(original=True)
            watermarked_area = cv2.addWeighted(self.original_destination, 1.0, self.original_logo, opacity, 0.0)
            self.original_img[self.original_top_y:self.original_bottom_y, self.original_left_x:self.original_right_x] = watermarked_area
            return cv2.cvtColor(self.original_img, cv2.COLOR_BGR2RGB)

    def format_original_for_writing(self):
        self.original_img_height, self.original_img_width = self.original_img.shape[:2]
        self.original_logo_height, self.original_logo_width = self.original_logo.shape[:2]
        if self.original_logo_height > self.original_img_height * 0.5:
            y = (self.original_img_height * 0.5) / self.original_logo_height
            self.original_logo = cv2.resize(self.original_logo, (int(self.original_logo_width*y), int(self.original_logo_height*y)))
            self.original_logo_resized = True
            self.original_logo_height, self.original_logo_width = self.original_logo.shape[:2]
        if self.original_logo_width > self.original_img_width * 0.5:
            x = (self.original_img_width * 0.5) / self.original_logo_width
            self.original_logo = cv2.resize(self.original_logo, (int(self.original_logo_width*x), int(self.original_logo_height*x)))
            self.original_logo_resized = True
            self.original_logo_height, self.original_logo_width = self.original_logo.shape[:2]


    def write_img(self, file):
        cv2.imwrite(f"{file}", self.img)

    def get_txt_pos(self, pos, **kwargs):
        """Returns an appropriate position given the string. i.e., 'center', 'top_left', etc."""
        self.update_dimensions()
        img_width = self.img_width if kwargs.get('original') is None else self.original_width
        img_height = self.img_height if kwargs.get('original') is None else self.original_height
        positions = {'center': (int(img_width*0.4), int(img_height*0.5)),
                     'top_center': (int(img_width*0.4), int(img_height*0.15)),
                     'bottom_center': (int(img_width*0.4), int(img_height*0.85)),
                     'right': (int(img_width*0.75), int(img_height*0.5)),
                     'top_right': (int(img_width*0.75), int(img_height*0.15)),
                     'bottom_right': (int(img_width*0.75), int(img_height*0.95)),
                     'left': (int(img_width*0.1), int(img_height*0.5)),
                     'top_left': (int(img_width*0.1), int(img_height*0.15)),
                     'bottom_left': (int(img_width*0.1), int(img_height*0.95)),
                     None: (int(img_height*0.5), int(img_width*0.5)), }
        return positions[pos]

    def refresh_array(self):
        """Refreshes the arrays of img and logo. Prevents saturation."""
        if self.img is not None:
            self.img = self.working_img.copy()
        if self.logo is not None:
            self.logo = self.working_logo.copy()

    def resize_update(self):
        print('resize_update() called.')
        if self.img_resized:
            if self.img_height > self.original_height:
                y = self.screen_height / self.img_height
                self.img = cv2.resize(self.img, (self.original_width, self.original_height))
                print(f'Image resized (height) in resize_update: {self.img.shape}')
                self.update_dimensions()
            if self.screen_width is not None and self.img_width > self.original_width:
                x = self.screen_width / self.img_height
                self.img = cv2.resize(self.img, (self.original_width, self.original_height))
                print(f'Image resized (width) in resize_update: {self.img.shape}')
                self.update_dimensions()
        if self.logo is not None:
            if self.logo_height > self.img_height * 0.5:
                y = self.logo_height / (self.img_height * 0.5)
                self.logo = cv2.resize(self.logo, (int(self.logo_width*y), int(self.logo_height*y)))
                self.update_dimensions()
            if self.logo_width > self.img_width * 0.5:
                x = self.logo_width / (self.img_width * 0.5)
                self.logo = cv2.resize(self.logo, (int(self.logo_width*x), int(self.logo_height*x)))
                self.update_dimensions()

    def center_logo(self, **kwargs):
        """Situates coordinates for the logo to appear at the center of the parent image. Returns nothing."""
        if kwargs.get('original'):
            self.original_center_y = int(self.original_img_height * 0.5)
            self.original_center_x = int(self.original_img_width * 0.5)
            self.calculate_destination(original=True)
            return
        self.update_dimensions()
        self.center_y = int(self.img_height * 0.5)
        self.center_x = int(self.img_width * 0.5)
        self.calculate_destination()

    def center_bottom_logo(self, **kwargs):
        """Situates coordinates for the logo to appear at the center of the parent image. Returns nothing."""
        if kwargs.get('original'):
            self.original_center_y = int(self.original_img_height * 0.75)
            self.original_center_x = int(self.original_img_width * 0.5)
            self.calculate_destination(original=True)
            return
        self.update_dimensions()
        self.center_y = int(self.img_height * 0.75)
        self.center_x = int(self.img_width * 0.5)
        self.calculate_destination()

    def center_top_logo(self, **kwargs):
        """Situates coordinates for the logo to appear at the center of the parent image. Returns nothing."""
        if kwargs.get('original'):
            self.original_center_y = int(self.original_img_height * 0.25)
            self.original_center_x = int(self.original_img_width * 0.5)
            self.calculate_destination(original=True)
            return
        self.update_dimensions()
        self.center_y = int(self.img_height * 0.25)
        self.center_x = int(self.img_width * 0.5)
        self.calculate_destination()

    def left_logo(self, **kwargs):
        """Situates coordinates for the logo to appear at the center left of the parent image. Returns nothing."""
        if kwargs.get('original'):
            self.original_center_y = int(self.original_img_height * 0.5)
            self.original_center_x = int(self.original_img_width * 0.25)
            self.calculate_destination(original=True)
            return
        self.update_dimensions()
        self.center_y = int(self.img_height * 0.5)
        self.center_x = int(self.img_width * 0.25)
        self.calculate_destination()

    def top_left_logo(self, **kwargs):
        """Situates coordinates for the logo to appear at the top left of the parent image. Returns nothing."""
        if kwargs.get('original'):
            self.original_height
            self.original_center_y = int(self.original_img_height * 0.25)
            self.original_center_x = int(self.original_img_width * 0.25)
            self.calculate_destination(original=True)
            return
        self.update_dimensions()
        self.center_y = int(self.img_height * 0.25)
        self.center_x = int(self.img_width * 0.25)
        self.calculate_destination()

    def right_logo(self, **kwargs):
        """Situates coordinates for the logo to appear at the top right of the parent image. Returns nothing."""
        if kwargs.get('original'):
            self.original_center_y = int(self.original_img_height * 0.5)
            self.original_center_x = int(self.original_img_width * 0.75)
            self.calculate_destination(original=True)
            return
        self.update_dimensions()
        self.center_y = int(self.img_height * 0.5)
        self.center_x = int(self.img_width * 0.75)
        self.calculate_destination()

    def top_right_logo(self, **kwargs):
        """Situates coordinates for the logo to appear at the top right of the parent image. Returns nothing."""
        if kwargs.get('original'):
            self.original_center_y = int(self.original_img_height * 0.25)
            self.original_center_x = int(self.original_img_width * 0.75)
            self.calculate_destination(original=True)
            return
        self.update_dimensions()
        self.center_y = int(self.img_height * 0.25)
        self.center_x = int(self.img_width * 0.75)
        self.calculate_destination()

    def bottom_right_logo(self, **kwargs):
        """Situates coordinates for the logo to appear at the bottom right of the parent image. Returns nothing."""
        if kwargs.get('original'):
            self.original_center_y = int(self.original_img_height * 0.75)
            self.original_center_x = int(self.original_img_width * 0.75)
            self.calculate_destination(original=True)
            return
        self.update_dimensions()
        self.center_y = int(self.img_height * 0.75)
        self.center_x = int(self.img_width * 0.75)
        self.calculate_destination()

    def bottom_left_logo(self, **kwargs):
        """Situates coordinates for the logo to appear at the bottom left of the parent image. Returns nothing."""
        if kwargs.get('original'):
            self.original_center_y = int(self.original_img_height * 0.75)
            self.original_center_x = int(self.original_img_width * 0.25)
            self.calculate_destination(original=True)
            return
        self.update_dimensions()
        self.center_y = int(self.img_height * 0.75)
        self.center_x = int(self.img_width * 0.25)
        self.calculate_destination()

