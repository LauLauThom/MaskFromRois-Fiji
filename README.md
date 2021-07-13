# Generate Masks from Rois in Fiji

This plugin facilitates the generation of mask images (0/255) from image-regions outlined with ROIs for large datasets.  
It can be used for instance to generate ground-truth mask annotations.  
Annotated images can be single plane images or stacks with a single dimensions slider, HYPERSTACKS ARE CURRENTLY NOT SUPPORTED.  

This plugin should be called after annotating image-regions with ROIs, stored in the RoiManager.  
Single images or multiple images in a stack (or Virtual stack) can be annotated. In the latter case, the Z-Position of the Rois is used to associate them to the corresponding image.

For each image (or stack slice), a mask image is generated with regions outlined by rois represented by white-pixels (value=255), while the background area is black (value=0).
Overlapping ROIs will result in a single "white blob" in the mask. 

The plugin should be executed after having annotated all ROIs in an image, or all image-slices of a stack.  

The resulting mask images can be displayed and saved to disk, in one of the proposed format and to a directory of choice.    
Filenames for the mask should be identical to the original filename when available (read from the window title, or from the slice label).  
An optional suffix can be added to the filenames, for instance if you are saving the mask in the same directory than the images.  

__Example__:  
original.tiff  
with suffix *-mask* and `png` extension  
original-mask.png
