#!/usr/bin/env python
# coding: utf-8

# In[1]:


cd cocosynth-master


# In[2]:


import numpy as np
import json
import os
from itertools import combinations
from pathlib import Path
import requests
import csv
import numpy as np
from matplotlib import pyplot as plt
import cv2
import pprint


# In[3]:


from lxml import etree
import xml.etree.cElementTree as ET


# In[4]:


annotation="/instances_val2017"
path="coco/annotations"
from pycocotools.coco import COCO
coco=COCO('{}{}.json'.format(path,annotation))


# In[5]:


cats = coco.loadCats(coco.getCatIds())


# In[6]:


def getFiles(path='D:\cocosynth-master\coco\stop_sign'):
    files = os.listdir(path)
    for i in range(len(files)):
        files[i]=(files[i].split('.')[0]).lstrip("0")
    return files


# In[7]:


def getHeightWidth(imageIds):
    images = coco.loadImgs(imageIds)
    height= images[0]['height']
    width= images[0]['width']
    return height,width
    


# In[8]:


def getFileName(imageIds):
    images = coco.loadImgs(imageIds)
    filename=images[0]['file_name']
    return filename


# In[9]:


def getAnnotations(imageIds):
    images= coco.loadImgs(imageIds)
    for im in images:
        annIds = coco.getAnnIds(imgIds=im['id'], catIds=[1,13], iscrowd=None)
        anns=coco.loadAnns(annIds)
    return anns


# In[10]:


#Include a for loop before this step
def getBoundingBox(annotation):
    bbox=annotation["bbox"]
    x=bbox[0]
    y=bbox[1]
    w=bbox[2]
    h=bbox[3]
    return x,y,w,h    


# In[11]:


def getName(annotation):
    ide=annotation['category_id']
    name=cats[(ide-1)]['name']
    if name=='parking meter':
        return 'stop_sign'
    return name


# In[12]:


def getDepth():
    return str(3)


# In[13]:


def writeXML(folder,img,savedir):
    #Ensure if there is not diectory, then create a new one
    if not os.path.isdir(savedir):
        os.mkdir(savedir)
        
    height,width=getHeightWidth(img)
    depth=getDepth()
    filename=getFileName(img)
    ann=getAnnotations(img)
    
    
    annotation = ET.Element('annotation')
    ET.SubElement(annotation,'folder').text = folder
    ET.SubElement(annotation,"filename").text = filename
    ET.SubElement(annotation,'segmented').text='0'
    size=ET.SubElement(annotation,'size')
    ET.SubElement(size,'width').text=str(width)
    ET.SubElement(size,'height').text=str(height)
    ET.SubElement(size,'depth').text=str(depth)
    for i in range(len(ann)):
        x,y,w,h=getBoundingBox(ann[i])
        objname=getName(ann[i])
        ob=ET.SubElement(annotation,'object')
        ET.SubElement(ob,'name').text=objname
        ET.SubElement(ob,'pose').text="Unspecified"
        ET.SubElement(ob,'truncated').text="0"
        ET.SubElement(ob,'difficult').text="0"
        bbox=ET.SubElement(ob,'bndbox')
        ET.SubElement(bbox,'xmin').text=str(x)
        ET.SubElement(bbox,'ymin').text=str(y)
        ET.SubElement(bbox,'xmax').text=str(x+w)
        ET.SubElement(bbox,'ymax').text=str(y+h)
        
        
    xml_str = ET.tostring(annotation)
    root = etree.fromstring(xml_str)
    xml_str = etree.tostring(root, pretty_print=True)
    
    save_path = os.path.join(savedir, filename.replace('jpg', 'xml'))
    with open(save_path, 'wb') as temp_xml:
        temp_xml.write(xml_str)


# In[14]:


def main():
    files=getFiles()
    for pics in files:
        xml_str=writeXML(folder="stop_sign",img=int(pics),savedir='stop_sign_annotations')

        
    


# In[15]:


main()

