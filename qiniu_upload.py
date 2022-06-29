import os

from qiniu import Auth, put_file, etag

access_key = '_9AXty01pMpW1FseLSYoJBAf0as0rs7rgb2iyHfb'
secret_key = 'ufZTabeOcqaUZhbZFsdEh1_FhUQ3fa24Vf2eggxw'
q = Auth(access_key, secret_key)
bucket_name = '41d8cd98f00b204e9800998'

image_path = 'images'
for key in os.listdir(image_path):
    token = q.upload_token(bucket_name, key, 3600)
    localfile = f'{image_path}{os.sep}{key}'
    ret, info = put_file(token, key, localfile, version='v2')
    print(ret,info)