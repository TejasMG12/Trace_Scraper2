from Service.clarifaiScript import checkDrugFromImage
from Service.imgurClient import uploadImage


def imageUrlDetection(url):
    try:
        return  checkDrugFromImage(url)
    except Exception as e:
        print(e)
        return None

def imageFileDetection(filename):
    try:
        filename = filename.split()
        Imageurl =  uploadImage(f"Media/{filename[0]}/{filename[1]}")
        return  checkDrugFromImage(Imageurl), Imageurl
    except Exception as e:
        print (e)
        return None,""