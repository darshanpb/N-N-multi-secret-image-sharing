from PIL import Image as j
import imagehash
from tkinter import *
import os, random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import numpy as np
import hashlib
import scipy.misc
import cv2
import matplotlib.pyplot as plt
from skimage import color
from skimage import io
import matplotlib.image as imge
import base64
from numpy import zeros
from tkinter import filedialog
import numpy
import imageio
from skimage import img_as_ubyte
from timeit import Timer
import time

folder_selected = "/home/darshan/inputsf"
list=[]
l=os.listdir(folder_selected)
width = 500
height = 500
ext = ".png"
i=0
for image in l:
    if image.endswith('png') or image.endswith('jpg'):
        img1 = j.open(folder_selected+'/'+image).convert('L')
        img = img1.resize((width, height), j.ANTIALIAS)
        img.save("enc/inputs/input{}".format(i) + ext)
        i+=1

folder_selected = "enc/inputs"
l=os.listdir(folder_selected)
images={}
i=0
width=0
height=0
for image in l:
    if image.endswith('png') or image.endswith('jpg'):
        img1 = io.imread(folder_selected+'/'+image, as_gray=True)
        height,width=img1.shape
        img1 = img_as_ubyte(img1)
        images[i]=img1
        i+=1
new_image=zeros([height,width])

start = time.time()
for key in images:
    arr=images[key]
    for x in range(height):
        for y in range(width):
            new_image[x][y]=int(new_image[x][y]) ^int(arr[x][y] )
imageio.imwrite('xored.png',new_image)
#plt.imshow(new_image)
img=j.open('xored.png').convert('L')
hash = imagehash.average_hash(img)
#print(hash)
key=str(hash)
filename = "xored.png"
filename_out = "enc/cipher_enc"
format = "png"
def pad(data):
    return data + b"\x00"*(16-len(data)%16) 
    
def process_image(filename):
    # Opens image and converts it to RGB format for PIL
    im = j.open(filename)
    data = im.convert("L").tobytes() 
 
    # Since we will pad the data to satisfy AES's multiple-of-16 requirement, we will store the original data length and "unpad" it later.
    original = len(data) 
 
    # Encrypts using desired AES mode (we'll set it to ECB by default)
    #new = convert_to_RGB(aes_cbc_encrypt(key, pad(data))[:original]) 
    new=aes_cbc_encrypt(key, pad(data))[:original]
    # Create a new PIL Image object and save the old image data into the new image.
    im2 = j.new(im.mode, im.size)
    im2.putdata(new)
    #new_arr = img_as_ubyte(new_arr)
    #Save image
    im2.save(filename_out+"."+format, format)
    
def aes_cbc_encrypt(key, data, mode=AES.MODE_CBC):
    IV = "A"*16  #We'll manually set the initialization vector to simplify things
    aes = AES.new(key, mode, IV)
    new_data = aes.encrypt(data)
    return new_data
process_image(filename)
enc_image = j.open("enc/cipher_enc.png")
#plt.imshow(enc_image)
enc_image.mode
arr = np.asarray(enc_image)
rows,col=arr.shape
new_arr=zeros([rows,col])
#print(rows,col)
def ran(x,y,i,M,N,d1,d2):
    pix=arr[(x-d1*i)%M,(y-d2*i)%N]^arr[(x+d1*i)%M,(y+d2*i)%N]
    return pix
n=len(images)
d1=(int(width)-1)//(2*n)
d2=(int(height)-1)//(2*n)
d1=random.randint(1,d1)
d2=random.randint(1,d2)
w=rows
h=col
for i in range(1,n+1):
    new_arr=np.ones([rows,col])
    for x in range(rows):
        for y in range(col):
            new_arr[x][y]=ran(x,y,i,w,h,d1,d2)
    #new_arr = img_as_ubyte(new_arr)
    imageio.imwrite('enc/rs/R{}.png'.format(i), new_arr)
def gen_share(no):
    for i in range(no):
        r1=j.open("enc/rs/R{}.png".format(i+1))
        arr_r1 = np.asarray(r1)
        if i==(n-1):
            r2=j.open("enc/rs/R1.png")
        else:
            r2=j.open("enc/rs/R{}.png".format(i+2))
        arr_r2 = np.asarray(r2)
        img=images[i]
        arr_i1 = np.asarray(img)
        share=zeros([rows,col])
        for x in range(rows):
            for y in range(col):
                share[x][y]=int(arr_i1[x][y])^int(arr_r1[x][y])^int(arr_r2[x][y])
        #share = img_as_ubyte(share)
        imageio.imwrite('enc/shares/share{}.png'.format(i), share)
gen_share(n)
print("Time taken for darshan encode --> {}".format(time.time()-start))