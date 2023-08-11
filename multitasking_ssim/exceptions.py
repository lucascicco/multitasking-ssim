class ImageError(Exception):
    pass


class ImageAlreadyExistsError(ImageError):
    pass


class ImageDuplicateError(ImageError):
    pass
