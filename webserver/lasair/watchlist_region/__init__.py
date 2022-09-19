import io
import base64
from mocpy import MOC, World2ScreenMPL
import matplotlib.pyplot as plt


def bytes2string(bytes):
    """*convert byte to string and return*

    **Key Arguments:**

    - `bytes` -- the byte string to convert
    """
    base64_bytes = base64.b64encode(bytes)
    str = base64_bytes.decode('utf-8')
    return str


def string2bytes(str):
    """*convert string to bytes and return*

    **Key Arguments:**

    - `str` -- the str string to convert to string
    """
    base64_bytes = str.encode('utf-8')
    bytes = base64.decodebytes(base64_bytes)
    return bytes


def make_image_of_MOC(fits_bytes):
    """*generate a skyplot of the MOC file*

    **Key Arguments:**

    - `fits_bytes` -- to FITS file data
    """
    inbuf = io.BytesIO(fits_bytes)
    try:
        moc = MOC.from_fits(inbuf)
    except:
        return render(request, 'error.html', {'message': 'Cannot make MOC from given file'})

    notmoc = moc.complement()

    fig = plt.figure(111, figsize=(10, 5))
    with World2ScreenMPL(fig, fov=360 * u.deg, projection="AIT") as wcs:
        ax = fig.add_subplot(1, 1, 1, projection=wcs)
        notmoc.fill(ax=ax, wcs=wcs, alpha=1.0, fill=True, color="lightgray", linewidth=None)
        moc.fill(ax=ax, wcs=wcs, alpha=1.0, fill=True, color="red", linewidth=None)
        moc.border(ax=ax, wcs=wcs, alpha=1, color="red")

    plt.grid(color="black", linestyle="dotted")
    outbuf = io.BytesIO()
    plt.savefig(outbuf, format='png', bbox_inches='tight', dpi=200)
    bytes = outbuf.getvalue()
    outbuf.close()
    return bytes
