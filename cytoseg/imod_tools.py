#Copyright (c) 2008 Richard Giuly
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.


import struct
import pickle
import numpy


global indexOfFirstPoint
global sizeOfInt
global sizeOfFloat
global sizeOfPoint

indexOfFirstPointInContourChunk = 20
sizeOfInt = 4
sizeOfFloat = 4
sizeOfPoint = 3 * sizeOfFloat  


# todo: this should be in a module that cytoseg and imod tools both access
def readPointList(file):
    points = []
    
    pointList = pickle.load(file)
    
   
    for coordinateList in pointList:
        point = numpy.array(coordinateList)

        
        points.append(point)

    return points




def chunkSize(s, location):
    #global restOfFile
    # s is a string
    id = getIdAt(s, location)
    
    if id == 'OBJT':
        return 4 + 176
       
    elif id == 'CONT':
        psize = struct.unpack('>i', s[location+4:location+8]) #number of points in contour
        return 4 + 16 + (12 * psize[0])
    
    elif id == 'MESH':
        print "error: mesh handling not in the program yet"
        
    elif id == 'IEOF':
        #return EOF
        return 4

    elif id == 'IMAT':
        #restOfFile = s[location:]
        chunkSize = struct.unpack('>i', s[location+4:location+8])
        return 8 + chunkSize[0]

        
    else:
        chunkSize = struct.unpack('>i', s[location+4:location+8])
        return 8 + chunkSize[0]
    
    
#def readChunkAt(s, location)

def getIdAt(string, location):
    id = string[location:location+idLength]
    return id

def readInt(string):
    list = struct.unpack('>i', string)
    return list[0]
    
def readFloat(string):
    #print string
    list = struct.unpack('>f', string)
    #print list
    return list[0]

def readPoint(string):
    numberList = []
    for i in range(0, 3 * sizeOfFloat, sizeOfFloat): 
        numberList.append(readFloat(string[i:i+sizeOfFloat]))
    
    return numpy.array(numberList)
    
    

def readContourChunk(string):
    if getIdAt(string, 0) != 'CONT':
        print 'error: contour chunk should start with CONT'

            
    numPoints = readInt(string[4:4+sizeOfInt])
    print 'numPoints'
    print numPoints
    
    points = []
    for i in range(indexOfFirstPointInContourChunk, 
                   indexOfFirstPointInContourChunk + numPoints * sizeOfPoint, sizeOfPoint): 
        points.append(readPoint(string[i:i+sizeOfPoint]))

    return points
   

class Chunk:
    def __init__(self, text):
        self.text = text
    
    def __str__(self):
        return "Chunk" + self.text[:4]
        #return "%s chunk size %d" % (self.text[0:4], len(self.text))

    def __repr__(self):
        return "Chunk" + self.text[:4]
        #return "%s chunk size %d" % (self.text[0:4], len(self.text))

    
class ModelData:
    def __init__(self):
        self.id = '........'
        self.name = 'name' #char
        self.xmax = 100000 #int
        self.ymax = 100000 #int
        self.zmax = 100000 #int
        self.objsize = 0 #int, number of objects in the model
        self.flags = 0  #uint
        self.drawmode = 1  #int
        self.mousemode = 1 #int
        self.blacklevel = 0    #int
        self.whitelevel = 255  #int
        self.xoffset = 0  #float
        self.yoffset = 0  #float
        self.zoffset = 0  #float
        self.xscale = 1  #float
        self.yscale = 1  #float
        self.zscale = 1  #float
        self.object = 1 #int, current object
        self.contour = 1 #int, current contour
        self.point = 1 #int, current point
        self.res = 1   #int      
        self.thresh = 1 #int
        self.pixsize = 1 # float 
        self.units = 0 #int     
        self.csum = 0 #int
        self.alpha = 0 #float
        self.beta = 0  #float
        self.gamma = 0 #float
        
    formatString = '>8s128siiiiIiiiiffffffiiiiifiifff'
        
    def readFromString(self, s):
        data = struct.unpack(ModelData.formatString, s)
        (self.id, self.name, self.xmax, self.ymax, self.zmax, self.objsize,
         self.flags, self.drawmode, self.mousemode, self.blacklevel,
         self.whitelevel, self.xoffset, self.yoffset, self.zoffset,
         self.xscale, self.yscale, self.zscale, self.object, self.contour,
         self.point, self.res, self.thresh, self.pixsize, self.units,
         self.csum, self.alpha, self.beta, self.gamma) = data
    
    def makeString(self):
        return struct.pack(ModelData.formatString, self.id, self.name, self.xmax, self.ymax, self.zmax, self.objsize,
         self.flags, self.drawmode, self.mousemode, self.blacklevel,
         self.whitelevel, self.xoffset, self.yoffset, self.zoffset,
         self.xscale, self.yscale, self.zscale, self.object, self.contour,
         self.point, self.res, self.thresh, self.pixsize, self.units,
         self.csum, self.alpha, self.beta, self.gamma)
        
#todo: it would be better to have a list of the names of fields in structure and number of bytes and lets the program take care of reading them        
class ObjectData:
    def __init__(self):

       self.id = "chunk id"
       self.name = "object name"  # char, 64 characters 
       self.extra = "extra bytes" # uint, 64 bytes of extra data for future use
       self.contsize = 0 #int   Number of Contours in object.
       self.flags = 0 #uint      bit flags for object (IMOD_OBJFLAG...).
       self.axis = 0 #int       Z = 0, X = 1, Y = 2. (unused)
       self.drawmode = 0 #int   Tells type of scattered points to draw (unused)
       self.red = 1 #float        Color values, range is (0.0 - 1.0)
       self.green = 0 #float      
       self.blue = 0 #float       
       self.pdrawsize = 1 #int    Default radius in pixels of scattered points in 3D.
       self.symbol = 1 #uchar       Point Draw symbol in 2D, default is 1.
       self.symsize = 1 #uchar      Size of 2D symbol; radius in pixels.
       self.linewidth2 = 1 #uchar   Linewidth in 2-D view.
       self.linewidth = 1 #uchar    Linewidth in 3-D view.
       self.linesty = 0 #uchar      Line draw style, 0 = solid; 1 = dashed (unused).
       self.symflags= 0 #uchar     
       self.sympad = 0 #uchar       Set to 0, for future use.
       self.trans = 0 #uchar        Transparency, range is (0 to 100)
       self.meshsize = 0 #int     Number of meshes in object.
       self.surfsize = 1 #int     Max surfaces in object.

    formatString = '>4s64s64siIiiffficcccccccii'

    def readFromString(self, s):
        print self.formatString
        data = struct.unpack(self.formatString, s)
        
        (self.id, self.name, self.extra, self.contsize, self.flags,
         self.axis, self.drawmode, self.red, self.green, self.blue,
         self.pdrawsize, self.symbol, self.symsize, self.linewidth2,
         self.linewidth, self.linesty, self.symflags, self.sympad,
         self.trans, self.meshsize, self.surfsize) = data

    def makeString(self):
         return struct.pack(self.formatString, self.id, self.name, self.extra, self.contsize, self.flags,
                            self.axis, self.drawmode, self.red, self.green, self.blue,
                            self.pdrawsize, self.symbol, self.symsize, self.linewidth2,
                            self.linewidth, self.linesty, self.symflags, self.sympad,
                            self.trans, self.meshsize, self.surfsize)
          

    #def readFromString(self, s):
    #    partOfString = s[0:128+4*4]
    #    (self.name, self.xmax, self.ymax, self.zmax, self.objsize) = struct.unpack('>128siiii', partOfString)  
    
def readIMODString(s):
    chunks = []
    current = sizeOfModelDataStructure
    while current < len(s):
        sz = chunkSize(s, current)
        
        #print "%s chunk size %d" % (s[current:current+4], sz)
        
        #if s[current:current+4] == 'CONT':
        #    points = readContourChunk(s[current:current+sz])
        #    #print points
        #    contours.append(points)
        
        chunks.append(Chunk(s[current:current+sz]))

        #print Chunk(s[current:current+sz])

        if sz == EOF:
            break
        current += sz    
    
    return chunks
    
#    #firstChunkLocation = 240
#
#    contours = []
#    
#    current = sizeOfModelDataStructure
#    
#    while current < len(s):
#        sz = chunkSize(s, current)
#        
#        print "%s chunk size %d" % (s[current:current+4], sz)
#        
#        if s[current:current+4] == 'CONT':
#            points = readContourChunk(s[current:current+sz])
#            #print points
#            contours.append(points)
#        
#
#        if sz == EOF:
#            break
#        current += sz
#        
#    return contours
    
def makeContourForSingleSphere(pt, volumeShape, radiusOfSphere):
    psize = 1 # int, number of points in contour
    flags = 0 # uint
    time = 0  # int
    surf = 0  # int
    
    #points
    #pt = [10, 20, 30]  # floats
    
    id = 'CONT'
    #data = struct.pack('>iIiifff', psize, flags, time, surf, pt[1], 141-pt[0], pt[2])
    data = struct.pack('>iIiifff', psize, flags, time, surf, pt[0], volumeShape[1] - pt[1], pt[2])
    
    return id + data + makeSizeDataChunk(radiusOfSphere)   
        

def makeSizeDataChunk(radiusOfSphere):
    psize = 1  # assuming only one point
    
    id = 'SIZE'
    lengthIndicator = 4 * psize
    data = struct.pack('>if', lengthIndicator, radiusOfSphere)
    
    return id + data   




def makeIMODFile(filename, points, sphereRadius):
    
    IMODFileInsertPoints("template.imod", filename, points, sphereRadius)
    

def old_IMODFileInsertPoints(inputFilename, outputFilename, points, sphereRadius):
    #file = open('template.imod', "rb")
    
    file = open(inputFilename, 'rb')
    str = file.read()
    file.close()
    
    #objectDataStructureSize = 176
        
        
    #readImodFile(str)
    readImodString(str)
    
    #print makeContourForSingleSphere()
    
    md = ModelData()
    md.readFromString(str[0:sizeOfModelDataStructure])
    print md.id
    print md.name
    print md.objsize
    print md.makeString()
    md.objsize = 1
    
    sz = chunkSize(str, sizeOfModelDataStructure)
    print ("size of object data %d" % sz)
    od = ObjectData()
    od.readFromString(str[sizeOfModelDataStructure:sizeOfModelDataStructure+sz])
    print "object contours"
    print od.contsize
    print od.id

    od.contsize = len(points)
    
    #outFile = open('c:\\temp\\out.imod', 'wb')
    #outFile = open(filename + "_inserted", 'wb')
    outFile = open(outputFilename, 'wb')

    outFile.write(md.makeString())
    outFile.write(od.makeString())
    for p in points:
        outFile.write(makeContourForSingleSphere(p, sphereRadius))
    #outFile.write('IEOF')
    outFile.write(restOfFile)
    outFile.close()
    
    
    #template = str[0:firstChunkLocation]

#def indexOfFirstContourChunk(chunks):
#    for i in range(len(chunks)):
#        if chunks[i].type == 'CONT':
#            return i
        

def IMODFileInsertPoints(inputFilename, outputFilename, points, volumeShape, sphereRadius):
    #file = open('template.imod', "rb")
    
    file = open(inputFilename, 'rb')
    str = file.read()
    file.close()
    
    #objectDataStructureSize = 176
        
        
    #readImodFile(str)
    chunks = readIMODString(str)
    #i = indexOfFirstContourChunk(chunks)
    
    #print makeContourForSingleSphere()
    
    print chunks
    
    md = ModelData()
    md.readFromString(str[0:sizeOfModelDataStructure])
    print md.id
    print md.name
    print md.objsize
    #print md.makeString()
    md.objsize += 1
    
    sz = chunkSize(str, sizeOfModelDataStructure)
    print ("size of object data %d" % sz)
    od = ObjectData()
    od.readFromString(str[sizeOfModelDataStructure:sizeOfModelDataStructure+sz])
    print "object contours"
    print od.contsize
    print od.id

    od.contsize = len(points)
    
    #outFile = open('c:\\temp\\out.imod', 'wb')
    #outFile = open(filename + "_inserted", 'wb')
    outFile = open(outputFilename, 'wb')

    outFile.write(md.makeString())
    outFile.write(od.makeString())
    for p in points:
        outFile.write(makeContourForSingleSphere(p, volumeShape, sphereRadius))
    #outFile.write('IEOF')
    #outFile.write(restOfFile)
    
    # skips the first chunk (which is object data) because it has already been written to the file
    #for i in range(1, len(chunks)):
    #    outFile.write(chunks[i].text)


    for i in range(0, len(chunks)):
        outFile.write(chunks[i].text)

    
    outFile.close()
    
    
    #template = str[0:firstChunkLocation]

    
    
#pointsExample = [[10,20,30],[10,30,20],[20,20,20]]

def getAllContours(filename):
    file = open(filename, "rb")
    s = file.read()
    file.close()
    return readImodString(s)





#global restOfFile
#global sizeOfModelDataStructure
firstHeaderSize = 8
sizeOfModelDataStructure = firstHeaderSize + 128 + (26 * 4)
idLength = 4
EOF = -1

        
 
    
    
     
              
           
