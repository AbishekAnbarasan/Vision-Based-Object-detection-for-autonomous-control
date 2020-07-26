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


# In[3]:



import requests
import csv
import numpy as np
from matplotlib import pyplot as plt
import cv2
import pprint


# In[4]:


class cocoAPI():
    """It's used to create an instance of coco api"""  
    
    def __init__(self,annotation="/instances_val2017",path="coco/annotations"):
        self.annotation=annotation#Specifies which annotation file to download
        self.path=path#Specifies the located annotations file
        
    def instantiate(self):  
        from pycocotools.coco import COCO
        return(COCO('{}{}.json'.format(self.path,self.annotation)))


# In[5]:


class Info():        
    """ Creates an info object from the COCO annotations"""    
    
    def __init__(self):
        pass
    
    def create_coco_info(self):
        info = dict()
        info['description'] = input("Enter description : ")
        info['url'] = input("Enter url :")
        info['version'] = input("Enter version :")
        info['year'] = input("Enter year :")
        info['contributor'] = input("Enter contributor :")
        info['date_created'] = input("Enter date_created :")
        return info


# In[6]:


class License(): 
    """ Creates an License object from the COCO annotations"""
    
    def __init__(self):
        pass    
    
    def create_coco_license(self):
        license = dict()
        license['url'] = input("Enter License url :")
        license['id'] = input("Enter License id :")
        license['name'] = input("Enter License name :")
        return license


# In[7]:


class Category():
    """Creates category obejects from COCO annotations"""
    
    def __init__(self):
        pass
    
    def dispCategories(self):
        """This function displays and returns all the supercategories and it's child category in the chosen annotation file """
        
        cate=coco.cats
        dik={}
        for i in range(1,len(cate)+1):
            if i in cate.keys():
                if cate[i]["supercategory"] not in list(dik.keys()):
                    dik[cate[i]["supercategory"]]=[]    
                dik[cate[i]["supercategory"]].append(cate[i]["name"])
        pprint.pprint(dik)
        return(dik)
      
    def extractClass(self): 
        """This function returns the selected category name and its corresponding supercategory stored in extractedDict"""
        
        categoryDict=self.dispCategories()
        extractedDict={}
        print('\n')
        print("Select any category names displayed above and/or press enter key to end")
        print('\n')
        nameList=[]
        while True:
            i=input()
            if i=='':
                break
            nameList.append(i)
        self.nameList=nameList
        for name in nameList:
            for key, value in categoryDict.items(): 
                if name in value: 
                    extractedDict[name]=key
        return(extractedDict)
    
    def create_coco_categories(self,supercategory,category_id,name):
        """This method creates the categories dictionary in json file"""
        category={}
        category['supercategory'] = supercategory
        category['id'] = category_id
        category['name'] = name
        
        return category


# In[8]:


class Download():
    
    """This function is used to download all the classes specified to extract"""
    
    def __init__(self,nameList):
        self.nameList=nameList
    
    def download(self):
        """Writes the images to dwnlds folder as default"""  
        #label has all possible combinations of nameList
        label = sum([list(map(list, combinations(self.nameList, i))) for i in range(len(self.nameList) + 1)], [])
        label.pop(0)
        for comb in label:
            cats = coco.loadCats(coco.getCatIds())
            nms=[cat['name'] for cat in cats]
            catIds = coco.getCatIds(catNms=comb)
            imgIds = coco.getImgIds(catIds=catIds )
            images = coco.loadImgs(imgIds)
            for im in images:
                img_data = requests.get(im['coco_url']).content
                with open('coco/light/' + im['file_name'], 'wb') as handler:
                    handler.write(img_data)


# In[9]:


class AnnotationAndImages():
    """This class is used to instantiate the object that writes to json file the coco api given annotations and images"""
    
    def __init__(self,path='D:\cocosynth-master\coco\light',name=None):
        self.name=name
        self.path=path
    
    def getImageId(self):
        """This method gives names of images in the root directory that contains images""" 
        files = os.listdir(self.path)
        for i in range(len(files)):
            files[i]=(files[i].split('.')[0]).lstrip("0")
        self.files=files
    
    def annImage(self):
        annotations=[]
        images=[]
        catIds = coco.getCatIds(catNms=self.name)
        for ind in self.files:
            #Images
            img = coco.loadImgs(int(ind))
            images.append(img[0])
            
            #Annotations
            annIds = coco.getAnnIds(imgIds=int(ind), catIds=catIds, iscrowd=None)
            anns = coco.loadAnns(annIds)
            
            for j in range(len(anns)):
                annotations.append(anns[j])
                
        return annotations,images  


# In[10]:


class COCO_JSON(): 
    
    """The main class puts all other classes together""" 
    
    def __init__(self,dataDirectory,downLoadPath='D:\cocosynth-master\coco\light'):
        self.dataDirectory=dataDirectory#Specifies where to write the json file
        self.downLoadPath=downLoadPath
    
    
    def infoCreater(self):
        inf=Info()
        return (inf.create_coco_info())
    yes
    def licenseCreater(self):
        lic=License()
        tempLic=lic.create_coco_license()
        return [tempLic]
    
    def categoryCreator(self):
        categories=[]
        cat=Category()
        filteredClass=cat.extractClass()
        names=list(filteredClass.keys())
        
        categoryIdsByName = dict()
        categoryId = 1 #default value
        
        for i in names:
            categories.append(cat.create_coco_categories(filteredClass[i],categoryId,i))
            categoryIdsByName[i]=categoryId
            categoryId+=1
        
        self.mainList= cat.nameList
        return categories,categoryIdsByName
    
    def annotation_imageCreator(self):
        ann_Img=AnnotationAndImages(self.downLoadPath,self.mainList)
        ann_Img.getImageId()
        annotations,images = ann_Img.annImage()
        return annotations,images
        
    def main(self):
        info = self.infoCreater()
        licenses = self.licenseCreater()
        categories, categoryIdsByName = self.categoryCreator()
        self.annotation_imageCreator()
        annotations,images = self.annotation_imageCreator()

        jsonObject = {
            'info': info,
            'licenses': licenses,
            'images': images,
            'annotations': annotations, 
            'categories':categories
        }

        # Write the json to a file
        outputPath = Path(self.dataDirectory) / 'cocolight.json'
        with open(outputPath, 'w+') as outputFile:
            json.dump(jsonObject, outputFile)
        pprint.pprint(f'Annotations successfully written to file:\n{outputPath}')

        


# In[11]:


if __name__=='__main__':
    api=cocoAPI()
    coco=api.instantiate()
    instance=COCO_JSON("D:\cocosynth-master\coco",downLoadPath='D:\cocosynth-master\coco\light')
    instance.main()
    ques=input("Do you need to download the images (yes/no) ?")
    if ques =='yes':
        dwnld=Download(instance.mainList)
        dwnld.download()
        print("Download Successfull")

    

