from __future__ import division
import os
try:
    from PIL import Image
except ImportError:
    import Image

_RESULT_EXTENSIONS = {
    'png' : set(['svg', 'gif', 'png', 'bmp', 'pnm', 'pdf'])
}

def lookup_extension(original_extension):
    original_extension = original_extension.lower()
    for ext, original_exts in _RESULT_EXTENSIONS.iteritems():
        if original_extension in original_exts:
            return ext
    return 'jpg'

def autosize(image, max_width, max_height, digits=None):
    """
    Returns a tuple (width, height) chosen intelligently so that the
    maximum values (given in ``max_width`` and ``max_height``)
    are respected and the aspect ratio is preserved.

    :param image: The original ``PIL.Image.Image``
    :param int digits: Number of digits the resulting `width` and `height` shall
                       be rounded to (or ``-1`` if no rounding shall be done)

    (This function is completely stolen from stupFF, which is BSD licensed and
     can be found at http://github.com/jonashaag/stupff.)
    """
    # The following code could be expressed in about two lines, but I think
    # readability is much more important than performance/elegance here.

    width, height = image.size
    aspect_ratio = width / height

    # calculate the ratio of the image and would-be heights and widths
    # and go on with the highest of the both.
    if max_height and height >= max_height:
        heights_ratio = height / max_height
    else:
        heights_ratio = None
    if max_width and width >= max_width:
        widths_ratio = width / max_width
    else:
        widths_ratio = None

    if heights_ratio is widths_ratio is None:
        # do nothing. no maximums given that would matter in any way
        return image.size

    if heights_ratio > widths_ratio:
        h, w = max_height, width / heights_ratio
    else:
        w, h = max_width, height / widths_ratio

    if digits is not None:
        w, h = round(w, digits), round(h, digits)

    return w, h

def thumbnail(original_file, result_file, max_width=None, max_height=None):
    image = Image.open(original_file)
    width_height = autosize(image, max_width, max_height)
    if width_height == image.size:
        return original_file

    result_file += lookup_extension(os.path.splitext(original_file)[1])

    thumb = image.resize(width_height)
    try:
        thumb.save(result_file, optimize=True)
    except:
        # only images under a certain size can be optimized.
        # If they can't an exception will be raised (I could not figure out
        # _which_ exception, hence the "except:".
        # --> save without optimization
        thumb.save(result_file)
    return result_file
