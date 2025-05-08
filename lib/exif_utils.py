import piexif
from .utils import dms_to_dd

def get_exif_data(img_path):
    time_stamp = "未知"
    lat = None
    lon = None
    exposure = ""
    iso = ""
    fnumber = ""
    model = ""
    make = ""
    lens = ""

    with open(img_path, 'rb') as img_file:
        exif_dict = piexif.load(img_file.read())

    if 'Exif' in exif_dict and piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
        try:
            time_stamp = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8', 'ignore')
        except UnicodeDecodeError:
            time_stamp = "未知"

    # 曝光时间
    if 'Exif' in exif_dict and piexif.ExifIFD.ExposureTime in exif_dict['Exif']:
        exposure_val = exif_dict['Exif'][piexif.ExifIFD.ExposureTime]
        if isinstance(exposure_val, tuple) and len(exposure_val) == 2 and exposure_val[1] != 0:
            exposure = f"1/{int(1/exposure_val[0]*exposure_val[1])}" if exposure_val[0] < exposure_val[1] else f"{exposure_val[0]/exposure_val[1]:.2f}s"
        else:
            exposure = str(exposure_val)

    # ISO
    if 'Exif' in exif_dict and piexif.ExifIFD.ISOSpeedRatings in exif_dict['Exif']:
        iso = str(exif_dict['Exif'][piexif.ExifIFD.ISOSpeedRatings])

    # 光圈
    if 'Exif' in exif_dict and piexif.ExifIFD.FNumber in exif_dict['Exif']:
        fnum = exif_dict['Exif'][piexif.ExifIFD.FNumber]
        if isinstance(fnum, tuple) and fnum[1] != 0:
            fnumber = f"F{fnum[0]/fnum[1]:.1f}"
        else:
            fnumber = str(fnum)

    # 相机型号
    if '0th' in exif_dict and piexif.ImageIFD.Model in exif_dict['0th']:
        try:
            model = exif_dict['0th'][piexif.ImageIFD.Model].decode('utf-8', 'ignore')
        except Exception:
            model = str(exif_dict['0th'][piexif.ImageIFD.Model])
    if '0th' in exif_dict and piexif.ImageIFD.Make in exif_dict['0th']:
        try:
            make = exif_dict['0th'][piexif.ImageIFD.Make].decode('utf-8', 'ignore')
        except Exception:
            make = str(exif_dict['0th'][piexif.ImageIFD.Make])
    # 镜头型号
    if 'Exif' in exif_dict and piexif.ExifIFD.LensModel in exif_dict['Exif']:
        try:
            lens = exif_dict['Exif'][piexif.ExifIFD.LensModel].decode('utf-8', 'ignore')
        except Exception:
            lens = str(exif_dict['Exif'][piexif.ExifIFD.LensModel])

    if 'GPS' in exif_dict:
        gps_info = exif_dict['GPS']
        gps_latitude_ref = gps_info.get(piexif.GPSIFD.GPSLatitudeRef)
        gps_latitude = gps_info.get(piexif.GPSIFD.GPSLatitude)
        gps_longitude_ref = gps_info.get(piexif.GPSIFD.GPSLongitudeRef)
        gps_longitude = gps_info.get(piexif.GPSIFD.GPSLongitude)

        if gps_latitude_ref and gps_latitude:
            gps_latitude_ref = gps_latitude_ref.decode('utf-8', 'ignore')
            lat = dms_to_dd(gps_latitude, gps_latitude_ref)

        if gps_longitude_ref and gps_longitude:
            gps_longitude_ref = gps_longitude_ref.decode('utf-8', 'ignore')
            lon = dms_to_dd(gps_longitude, gps_longitude_ref)

    return time_stamp, lat, lon, exposure, iso, fnumber, make, model, lens
