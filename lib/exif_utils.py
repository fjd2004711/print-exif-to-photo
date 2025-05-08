import piexif
from .utils import dms_to_dd

def get_exif_data(img_path):
    time_stamp = "未知"
    lat = None
    lon = None
    aperture = "未知"
    iso = "未知"
    shutter_speed = "未知"

    with open(img_path, 'rb') as img_file:
        exif_dict = piexif.load(img_file.read())

    if 'Exif' in exif_dict and piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
        try:
            time_stamp = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8', 'ignore')
        except UnicodeDecodeError:
            time_stamp = "未知"

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

    if 'Exif' in exif_dict:
        exif = exif_dict['Exif']
        if piexif.ExifIFD.FNumber in exif:
            aperture = f"f/{exif[piexif.ExifIFD.FNumber][0] / exif[piexif.ExifIFD.FNumber][1]}"
        if piexif.ExifIFD.ISOSpeedRatings in exif:
            iso = str(exif[piexif.ExifIFD.ISOSpeedRatings])
        if piexif.ExifIFD.ExposureTime in exif:
            exposure_time = exif[piexif.ExifIFD.ExposureTime]
            if exposure_time[0] / exposure_time[1] < 1:
                shutter_speed = f"1/{int(exposure_time[1] / exposure_time[0])}"
            else:
                shutter_speed = f"{exposure_time[0] / exposure_time[1]}s"

    return time_stamp, lat, lon, aperture, iso, shutter_speed