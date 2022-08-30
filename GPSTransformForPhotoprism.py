# -*- coding: utf-8 -*-
import json
import urllib
import math
import os
import sys

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方

def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
   # if out_of_china(lng, lat):
   #     return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]

def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)

def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def get_img_gps(imgs):
    command = 'exiftool -T -GPSLatitude -n '+imgs
    lat = os.popen(command).read()
    command = 'exiftool -T -GPSLongitude -n '+imgs
    lng = os.popen(command).read()

    lat_dec = float(lat)
    lng_dec = float(lng)

    return(lat_dec, lng_dec)

def get_img_exif(imgs):

    command = 'exiftool -T -artist -GPSLatitude -GPSLongitude -n '+imgs
    exif = os.popen(command).read().strip('\n').split('\t')

    author = exif[0]

    lat_dec = float(exif[1])
    lng_dec = float(exif[2])

    return(author, lat_dec, lng_dec)


def imgGPSgcjTOwgs(img):
    author, lat, lng = get_img_exif(img)
    print(author,lng,lat)
    if 'GPSTransformed' in author:
        return
    lngwgs,latwgs = gcj02_to_wgs84(lng,lat)
    print(lngwgs,latwgs)
    command = 'exiftool -P -artist=byGPSTransformed -GPSLongitudeRef=E -GPSLongitude=' + \
        str(lngwgs) + ' -GPSLatitudeRef=N -GPSLatitude=' + \
        str(latwgs) + ' -overwrite_original ' + img
    command2 = 'exiftool -P -artist=byGPSTransformed -GPSLongitudeRef=E -GPSLongitude=' + \
        str(lngwgs) + ' -GPSLatitudeRef=N -GPSLatitude=' + \
        str(latwgs) + ' ' + img
    print(command)
    a = os.system(command)
    print(a)

def imgGPSbdTOwgs(img):
    author, lat, lng = get_img_exif(img)
    print(author,lng,lat)
    if 'GPSTransformed' in author:
        return
    lngwgs,latwgs = bd09_to_wgs84(lng,lat)
    print(lngwgs,latwgs)
    command = 'exiftool -P -artist=byGPSTransformed -GPSLongitudeRef=E -GPSLongitude=' + \
        str(lngwgs) + ' -GPSLatitudeRef=N -GPSLatitude=' + \
        str(latwgs) + ' -overwrite_original ' + img
    command2 = 'exiftool -P -artist=byGPSTransformed -GPSLongitudeRef=E -GPSLongitude=' + \
        str(lngwgs) + ' -GPSLatitudeRef=N -GPSLatitude=' + \
        str(latwgs) + ' ' + img
    print(command)
    a = os.system(command)
    print(a)


def get_imgfiles(dirs):
    files = []
    for filepath, dirnames, filenames in os.walk(dirs):
        for filename in filenames:
            # print(os.path.join(filepath,filename))
            if '.jpg' in filename:
                files.append(os.path.join(filepath, filename))
    return files


if __name__ == '__main__':
    dir = './'
    files = get_files(dir)
    print('Total files: ',len(files))
    for file in files:
        if '.jpg' in file:
            print(file)
            imgGPSgcjTOwgs(file)
    cmmand = 'mv *.jpg /root/photoprism/Import/'
    res = os.popen(cmmand)  
    print(res)