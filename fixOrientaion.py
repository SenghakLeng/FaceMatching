from PIL import Image, ExifTags

def fixImage(image, size =(640, 640)):

    def get_image_orientation(image):
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    exif = image._getexif()
                    if exif is not None:
                        exif_value = exif.get(orientation)
                        if exif_value is not None:
                            return exif_value
        except:
            pass
        return 1


    def fix_image_orientation(image):
        orientation = get_image_orientation(image)
        if orientation == 1:
            return image
        elif orientation == 3:
            return image.rotate(180, expand=True)
        elif orientation == 6:
            return image.rotate(270, expand=True)
        elif orientation == 8:
            return image.rotate(90, expand=True)
        else:
            return image


    def crop_to_square(image):
        width, height = image.size
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = (width + min_dim) // 2
        bottom = (height + min_dim) // 2
        cropped_image = image.crop((left, top, right, bottom))
        return cropped_image

    image = Image.open(image)
    w, h =image.size
    image = fix_image_orientation(image)
    if w > size[0]:
        cropped_image = crop_to_square(image).resize(size)
    else: 
        cropped_image = image.resize(size)
    return cropped_image


