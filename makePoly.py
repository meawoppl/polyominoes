import hashlib
from scipy import *
from scipy import ndimage, misc
from pylab import *

startGrid = zeros((3,3))
startGrid[1,1] = 1

def makeSinglePixMargins(inputBinaryImage):
    cropped = cropMin(inputBinaryImage)
    return addPxBuffer(cropped)

def addPxBuffer(inputBinaryImage):
    embedIn = zeros((inputBinaryImage.shape[0] + 2, inputBinaryImage.shape[1] + 2))
    embedIn[1:-1,1:-1] = inputBinaryImage[:,:]
    return embedIn

def offsetToNonZero(oneDeeArray):
    for x in range(oneDeeArray.shape[0]):
        if oneDeeArray[x] > 0: break

    return x

def cropMin(inputBinaryImage):
    rowSum = inputBinaryImage.sum(axis = 1)
    colSum = inputBinaryImage.sum(axis = 0)

    l = offsetToNonZero(rowSum)
    r = rowSum.size - offsetToNonZero(rowSum[::-1])

    t = offsetToNonZero(colSum)
    b = colSum.size - offsetToNonZero(colSum[::-1])

    return inputBinaryImage[ l:r, t:b]


def findPotentialAggregates(binaryInputImage):
    padded = makeSinglePixMargins(binaryInputImage)
    dialated = ndimage.binary_dilation(padded)

    delta = dialated - padded
    
    newPoints = []
    for point, value in ndenumerate(delta):
        if value: 
            newPoints.append(point)
  
    returnImages = []
    for point in newPoints:
        newImage = padded.copy()
        newImage[point] = 1
        returnImages.append(newImage)

    return returnImages


def tileAFew(listOfImages):
    paddedImages = [makeSinglePixMargins(img) for img in listOfImages]

    maxDim = max([max(img.shape)-1 for img in paddedImages])

    tileSize = maxDim

    nTiles = ceil(sqrt(len(listOfImages)))
    
    newImage = zeros((nTiles * tileSize, nTiles * tileSize))
    for n, img in enumerate(listOfImages):
        xTile = (n %  nTiles)
        yTile = (n // nTiles)
        
        xPos = xTile * tileSize
        yPos = yTile * tileSize

        newImage[xPos:xPos + img.shape[0], yPos:yPos + img.shape[1]] = img[:,:]
        
    return addPxBuffer(newImage)


def inflateImage(inputImage, n=2):
    newImage = zeros(inputImage.shape[0] * n, inputImage.shape[1] * n)
    
    for x in range(n):
        for y in range(n):
            newImage[x::n,y::n] = inputImage

    return newImage



def showAll(listOfImages):
    tiledImage = tileAFew(listOfImages)
    print tiledImage.shape
    pcolor(tiledImage)
    axis("image")
    savefig("tooBig.png")

    # show()

def allTransformations(image):
    return [image[:,:], image[:,::-1], image[::-1,:], image[::-1,::-1], image.T[:,:], image.T[:,::-1], image.T[::-1,:], image.T[::-1,::-1]]


def imageHashes(image):
    castImage = image.astype(uint8)
    ndarrayHash = lambda nda : hashlib.md5(nda.tostring() + str(nda.shape)).hexdigest()

    hashes = set()
    map(hashes.add, 
        map(ndarrayHash, allTransformations(castImage)))

    return hashes


class UniqueImageCollecter(object):
    def __init__(self):
        self.images = []
        self.hashSet = set()

    def add(self, image):
        hashes = imageHashes(cropMin(image))
        
        if self.hashSet.isdisjoint(hashes):
            self.images.append(image)
            self.hashSet.update(hashes)    
        
    def update(self, imageList):
        for image in imageList:
            self.add(image)


def findNextLargerSet(imageList):
    nextSet = UniqueImageCollecter()
    for n, img in enumerate(imageList):
        if (n+1) % 1000 == 0: print n+1, " of ", len(imageList)
        nextSet.update( findPotentialAggregates(img) )
        
    print 
    return nextSet.images


listOfImageSets = []
listOfImageSets.append([startGrid])

allList = []


n = 19
for x in range(1,n):
    print "*" * 20
    print x
    print "*" * 20
    print 
    lastSet = listOfImageSets[-1]
    nextSet = findNextLargerSet(lastSet)
    listOfImageSets.append(nextSet)
    allList += nextSet

    misc.imsave("up_to_%i.png" % (x+1), tileAFew(nextSet))



for n, imageList in enumerate(listOfImageSets):
    print n+1, len(imageList)

for n, imageList in enumerate(listOfImageSets):
    print len(imageList), ",",

#showAll(allList)

