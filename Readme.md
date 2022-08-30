1、国内部分手机拍照的GPS坐标用了GCJ坐标体系，脚本实现了读取目录下的jpg格式照片的GPS信息，并将GPS坐标转换为WGS格式坐标，并将照片移动到 /root/photoprism/Import/ 目录。便于photoprism导入。

2、脚本基于python3、Centos，需要安装exiftoo
