"""
This plugin facilitates the generation of mask images (semantic) from image-regions outlined with grouped ROIs for large datasets.
Annotated images can be single plane images or stacks with a single dimensions slider.
HYPERSTACKS ARE CURRENTLY NOT SUPPORTED.
This plugin should be called after annotating image-regions with ROIs of different groups, stored in the RoiManager.
Single images or multiple images in a stack (or Virtual stack) can be annotated. In the latter case, the Z-Position of the Rois is used to associate them to the corresponding image.

For each image (or stack slice), a mask image is generated with regions outlined by rois represented by colored pixels (value>=1), while the background area is black (value=0).
Overlapping ROIs will result in the ROI with the highest group number overlapping the other in the mask. 

The plugin should be executed after having annotated all ROIs in an image, or all image-slices of a stack.
"""
#@ ImagePlus imp
#@ RoiManager rm
#@ PrefService prefs

from ij.gui import Overlay, GenericDialog
from fiji.util.gui import GenericDialogPlus
from ij     import IJ, ImageStack, ImagePlus
from ij.process import ByteProcessor, ImageProcessor
from ij.plugin import LutLoader
import os
from FilenameGetter import getImageName, getSliceName

gui = GenericDialog("Mask from Roi")
gui.addCheckbox("Show_mask(s)", prefs.getInt(None, "showMask", True))
gui.addToSameRow()
gui.addCheckbox("Save_mask(s)", prefs.getInt(None, "saveMask", False))
gui.addDirectoryField("Save_in directory", prefs.get(None, "directory", ""))
gui.addStringField("Suffix for filename (optional)", prefs.get(None, "suffixname", ""))
gui.addChoice("Save_mask_as", ["tif", "tiff", "png", "jpg", "gif", "bmp"], prefs.get(None, "saveas", "tif"))

gui.addMessage("""If you use this plugin please cite:
  
Laurent Thomas, & Pierre Trehin. (2021, July 22)
github : LauLauThom/MaskFromRois-Fiji
Masks from ROIs plugins for Fiji - initial release (Version 1.0.0)
Zenodo. http://doi.org/10.5281/zenodo.5121890""")

gui.addHelp(r"https://imagej.github.io/plugins/masks-from-rois")

gui.showDialog()

if gui.wasOKed():
	show_mask = gui.getNextBoolean()
	save_mask = gui.getNextBoolean()
	outDir = gui.getNextString()
	suffix = gui.getNextString()
	extension = gui.getNextChoice()

prefs.put(None, "showMask", show_mask)
prefs.put(None, "saveMask", save_mask)
prefs.put(None, "directory", outDir)
prefs.put(None, "suffixname", suffix)
prefs.put(None, "saveas", extension)

if imp.isHyperStack():
	IJ.error("Hyperstack are not supported, use single-slider stack instead.\n" +
			 "Or get in touch if you would really benefit from it.")
	raise Exception("Active image is a hyperstack")
	# Could support hyperstack in the future but complicated, need to convert from slice index to hyperstack position and check roi CZT positions
	# The ROI CZT Position can be 0 for a given dimension, meaning it's appearing on all slices of this dimension

if rm.getCount() == 0:
	msg = "No ROIs in the RoiManager."
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

	mask = ByteProcessor(imp.getWidth(), imp.getHeight()) # create a black 8-bit image to use as mask to paint over 

	# Group the rois of this slice into an Overlay
	for roi in listRois:

		if roi.getGroup() > 254:
			IJ.error(" You set an Roi group number over 254. Only Roi group numbers under 254 are supported.")
			raise Exception(" Invalid Roi group number for display in an 8 bit image due to 0 being taken by background")

		if (stackSize>1) and (roi.getPosition() != sliceIndex):
			# if stackSize = 1 ie single plane image, we just take all rois (which all have a position of 0 by the way)
			continue # skip this ROI

		ImageProcessor.setColor( mask, roi.getGroup()+1 ) # mask.setColor did not work with integer, always expecting a Color so use Class.method(instance, parameter) instead
		mask.fill(roi)

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
	
	# Set glasbey LUT
	pathLut = os.path.join(IJ.getDirectory("imagej"),'luts','glasbey_on_dark.lut')
	LUT    = LutLoader.openLut(pathLut)
	impMasks.setLut(LUT)
	
	impMasks.show()