"""
This plugin facilitates the generation of mask images (0/255) from image-regions outlined with ROIs for large datasets.
Annotated images can be single plane images or stacks with a single dimensions slider.
HYPERSTACKS ARE CURRENTLY NOT SUPPORTED.
This plugin should be called after annotating image-regions with ROIs, stored in the RoiManager.
Single images or multiple images in a stack (or Virtual stack) can be annotated. In the latter case, the Z-Position of the Rois is used to associate them to the corresponding image.

For each image (or stack slice), a mask image is generated with regions outlined by rois represented by white-pixels (value=255), while the background area is black (value=0).
Overlapping ROIs will result in a single "white blob" in the mask. 

The plugin should be executed after having annotated all ROIs in an image, or all image-slices of a stack.
The script parameters define default values via value = , to avoid having null references when a field is empty
"""
#@ Boolean (label="Show mask(s)", value=true) show_mask
#@ Boolean (label="Save mask(s)", value=false) save_mask
#@ File    (label="Save mask(s) in directory", style="directory", value="") outDir
#@ String  (label="Filename suffix (optional)", value="") suffix
#@ String  (label="Save masks as", choices={"tif", "tiff", "png", "jpg", "gif", "bmp"}, value="tif") extension
#@ ImagePlus imp
#@ RoiManager rm
from ij.gui import Overlay
from ij     import IJ, ImageStack, ImagePlus
import os
from FilenameGetter import getImageName, getSliceName

if imp.isHyperStack():
	IJ.error("Hyperstack are not supported, use single-slider stack instead.\n" +
			 "Or get in touch if you would really benefit from it.")
	raise Exception("Active image is a hyperstack")
	# Could support hyperstack in the future but complicated, need to convert from stlice index to hyperstack position and check roi CZT positions
	# The ROI CZT Position can be 0 for a given dimension, meaning it's appearing on all slices of this dimension

if rm.getCount() == 0:
	msg = "No ROIs in the RoiManager."
	IJ.error(msg)
	raise Exception(msg)

outDir = outDir.getPath()

# Check that the directory field is not empty when saving
if save_mask and len(outDir)==0:
	msg = "Saving is selected but no directory was provided."
	IJ.error(msg)
	raise Exception(msg)

# Check that we are not overwriting the original images
# This might happen if the output directory == image directory and no suffix is used
# in practice overwriting the original images would require that they also have a tiff extension but we dont check it here 
fileInfo = imp.getOriginalFileInfo()

if save_mask and fileInfo : # sometimes fileInfo is null
	
	sameDir  = fileInfo.directory[:-1] == outDir # -1 to not take the last \
	
	if sameDir and len(suffix)==0: # ie saving the mask in the image directory with identical image names 
		IJ.error("""Please select another output directory or add a filename suffix.
					Current settings could otherwise result in having the mask images overwriting the images.
					""")
		raise Exception("Prevents overwritting the images when output directory = image directory and empty suffix.")


listRois  = rm.getRoisAsArray()
stackSize = imp.getStackSize()

if show_mask:
	stackOfMasks = ImageStack() # one mask-slice per image-slice

imp.deleteRoi() # remove any active ROI not in the ROI manager
for sliceIndex in range(1, stackSize+1): # slice index ranges [1, stackSize] (hence +1 to have it included)

	overlay = Overlay() # create a new Overlay for each image, to generate a new mask

	# Group the rois of this slice into an Overlay
	for roi in listRois:

		if (stackSize>1) and (roi.getPosition() != sliceIndex):
			# if stackSize = 1 ie single plane image, we just take all rois (which all have a position of 0 by the way)
			continue # skip this ROI

		overlay.add(roi)

	# Create a mask from this Overlay
	imp.setOverlay(overlay)
	mask = imp.createRoiMask()

	if show_mask:
		stackOfMasks.addSlice(mask)
	
	if save_mask :
		filename = getImageName(imp) if stackSize==1 else getSliceName(imp, sliceIndex) 
		filename = os.path.splitext(filename)[0] + suffix +"." + extension # use original filename followed by suffix + .extension
		
		filepath = os.path.join(outDir, filename)
		IJ.save(ImagePlus("mask", mask), filepath)
	
	
# Finally show the stack of mask if asked for
if show_mask:
	impMasks = ImagePlus("Masks", stackOfMasks)
	impMasks.show()