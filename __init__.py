from __future__ import division
import os
import tinymagick


PROPOSED_FORMATS = {
    'png' : set(['svg', 'gif', 'png', 'bmp', 'pnm', 'pdf'])
}

def normalize_extension(ext):
    return str(ext).lstrip('.').lower()

def recommend_thumbnail_format(image_format):
    image_format = normalize_extension(image_format)
    for recommended_format, source_formats in PROPOSED_FORMATS.iteritems():
        if image_format in source_formats:
            return recommended_format
    # fallback to jpg if no better solution could be found
    return 'jpg'

def autosize(image, max_width, max_height, digits=None, as_int=False):
    """
    Returns a tuple (width, height) chosen intelligently so that the
    maximum values (given in ``max_width`` and ``max_height``)
    are respected and the aspect ratio is preserved.

    :param image: The original ``tinymagick.Image``
    :param int digits: Number of digits the resulting `width` and `height` shall
                       be rounded to (or ``-1`` if no rounding shall be done)

    (This function is completely stolen from stupFF, which is BSD licensed and
     can be found at http://github.com/jonashaag/stupff.)
    """
    # The following code could be expressed in about two lines, but I think
    # readability is much more important than performance/elegance here.
    aspect_ratio = image.width / image.height

    # calculate the ratio of the image and would-be heights and widths
    # and go on with the highest of the both.
    if max_height and image.height >= max_height:
        heights_ratio = image.height / max_height
    else:
        heights_ratio = None
    if max_width and image.width >= max_width:
        widths_ratio = image.width / max_width
    else:
        widths_ratio = None

    if heights_ratio is widths_ratio is None:
        # do nothing. no maximums given that would matter in any way
        return (image.width, image.height)

    if heights_ratio > widths_ratio:
        h, w = max_height, image.width / heights_ratio
    else:
        w, h = max_width, image.height / widths_ratio

    if as_int:
        assert digits is None, "`digits` can't be set if `as_int` is True"
        w = int(round(w, 0))
        h = int(round(h, 0))

    elif digits is not None:
        w, h = round(w, digits), round(h, digits)

    return w, h

def thumbnail(original_file, result_file, max_width=None, max_height=None):
    image = tinymagick.Image(original_file)
    width, height = autosize(image, max_width, max_height, as_int=True)
    if (width, height) == (image.width, image.height):
        return original_file

    result_file += recommend_thumbnail_format(
        os.path.splitext(original_file)[1]
    )
    image.thumbnail(result_file, width, height)
    return result_file
