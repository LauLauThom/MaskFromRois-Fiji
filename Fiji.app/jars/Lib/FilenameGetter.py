"""
Contains utility function to recover a filename suitable for saving from different type of images in ImageJ/Fiji
Ex: single plane image, stack and hyperstacks

This script can be run in the script interpreter too for testing. It will use the active image.
"""

def getImageName(imagePlus):
	"""
	Try to recover the filename of the image if opened from disk, otherwise make up a filename from the window title.
	Rather targetting non-stack images.
	"""
	
	# Get image name 
	imageName = ""
	fileInfo = imagePlus.getOriginalFileInfo()
	if fileInfo: 
		imageName = fileInfo.fileName
	
	if imageName=="Untitled" or not imageName: 
		splitted = imagePlus.getWindow().getTitle().split()
		imageName = splitted[0].replace(" ","") # remove whitespaces, expected for a filename

	return imageName


def getSliceName(imagePlus, sliceIndex):
	"""
	Try to get the name of the slice-image at the given index of a stack image.
	If inexistent, a slice name is made up as "C:c, Z:z, T:t" for hyperstacks or "Slice x" for single slider stacks
	"""
	stack = imagePlus.getStack() 
		
	if (sliceIndex<1) or (sliceIndex>stack.getSize()):
		raise ValueError("Slice index for stacks must be between 1 and stack-size.")
	
	# Slice name
	sliceName = stack.getSliceLabel(sliceIndex) 
	
	if sliceName is not None: 
		sliceName = sliceName.split('\n',1)[0] # can be useful when ImagesToStack/Import Sequence was used
	
	else: # empty slice label
		
		if imagePlus.isHyperStack(): 
			c,z,t = imagePlus.convertIndexToPosition(sliceIndex)
			sliceName = "C:{},Z:{},T:{}".format(c,z,t)
		
		else: # 1D stack
			# Can be tested with the mri-stack
			sliceName = 'Slice ' + str(imagePlus.currentSlice)	 
	
	return sliceName


# TEST
if __name__ in ['__builtin__', '__main__']:
	from ij import IJ
	
	imp = IJ.getImage()
	print "Image name", getImageName(imp)
	#print imp.getStack().getSliceLabel(1)
	
	index = 2 
	print "Slice name", getSliceName(imp, index)