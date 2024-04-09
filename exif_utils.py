import piexif
from utils import dms_to_dd

def get_exif_data(img_path):
    time_stamp = "未知"
    lat = None
    lon = None

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

    return time_stamp, lat, lon
