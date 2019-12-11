import os
import json
import queue
import threading

import requests
from PIL import Image
from contextlib import closing

import _thread
import time


def fetch_img_func(q):
    while True:
        try:
            index,url = q.get_nowait()# 不阻塞的读取队列数据
        except Exception as e:
            print (e)
            break
        # print ('Current Thread Name Runing %s ... ' % threading.currentThread().name)
        print("processing %s"% index)
        res = requests.get(url, stream=True)
        if res.status_code == 200:
            save_img_path ='pic/%s.png'%index
            # 保存下载的图片
            with open(save_img_path, 'wb') as fs:
                for chunk in res.iter_content(1024):
                    fs.write(chunk)


def convert_images_to_pdf(img_path, pdf_path):
    file_list = os.listdir(img_path)
    pic_name = []
    im_list = []
    for x in file_list:
        if "jpg" in x or 'png' in x or 'jpeg' in x:
            pic_name.append(img_path + x)
    new_pic = []
    for x in pic_name:
        if "jpg" in x:
            new_pic.append(x)
    for x in pic_name:
        if "png" in x:
            new_pic.append(x)
    print("hec", new_pic)
    im1 = Image.open(new_pic[0])
    new_pic.pop(0)
    for i in new_pic:
        img = Image.open(i)
        # im_list.append(Image.open(i))
        if img.mode == "RGBA":
            img = img.convert('RGB')
            im_list.append(img)
        else:
            im_list.append(img)
    im1.save(pdf_path, "PDF", resolution=100.0, save_all=True, append_images=im_list)
    print("输出文件名称：", pdf_path)


def process_json(json_path):
    with open(json_path, 'r') as f:
        data = json.loads(f.read())
        print(data["data"]["presentationSlides"]["Slides"])
        data = list(map(lambda x: (x["Index"], x["Cover"]), data["data"]["presentationSlides"]["Slides"]))
        print(data)

        q = queue.Queue()
        for d in data:
            q.put(d)

        num = 10  # 线程数
        threads = []
        for i in range(num):
            t = threading.Thread(target=fetch_img_func, args=(q,), name="child_thread_%s" % i)
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()


if __name__ == '__main__':
    process_json("tmp.json")
    convert_images_to_pdf("pic/", "total.pdf")
