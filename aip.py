""" 
	Astronomical Image Processing

	Group 16

	Marcio de Souza Campos 8937461
	Marly da Cruz Claudio  8936885
	Robson Marques Pessoa  8632563 

"""

from astropy.io import fits
import numpy as np
import cv2

# normalize the .fits matrix data values between 0 and 255, transpose 
# the matrix and set the picture size to 750x750

def normalize(img):

	n = img / (np.max(img) / 255.0)
	n = cv2.resize(n, (750, 750), interpolation = cv2.INTER_CUBIC)
	n = n.transpose()

	return n

# applies a logarithm filter

def logarithmFilter(img):

	(minimg, maximg, tmp1, tmp2) = cv2.minMaxLoc(img)
	log = cv2.log(img + 1)
	log = cv2.multiply(log, (255 / np.log(1 + maximg)))
	log = cv2.convertScaleAbs(log)
	log = cv2.normalize(log, log, 0, 255, cv2.NORM_MINMAX)

	return log

# converts the grayscale images to the hsv color space

def gray2hsv(img):

    img = np.expand_dims(img, axis = 2)
    hsv = np.zeros((750, 750, 2), dtype = np.uint8)
    hsv = np.append(hsv, img, axis = 2)

    return hsv

# input:
#	you may input 2 or 3 image files of the same object ()

fileName1 = input("1st image file name: ")
wl1 = int(input("1st image wavelength: "))
img1 = fits.getdata(fileName1)

fileName2 = input("2nd image file name: ")
wl2 = int(input("2nd image wavelength: "))
img2 = fits.getdata(fileName2)

fileName3 = input("3rd image file name (type 0 if there is no 3rd image): ")
if fileName3 != "0":
	wl3 = int(input("3rd image wavelength: "))
	img3 = fits.getdata(fileName3)
	flagThird = 1
else:
	flagThird = 0

print("\nDo you want to save the final picture as a PNG file? (y/n)")
flagSave = input()
if flagSave == "y":
	finalName = input("Final picture file name: ")

# pre-processing

band1 = normalize(img1)
band1 = logarithmFilter(band1)

band2 = normalize(img2)
band2 = logarithmFilter(band2)

# if there is only 2 input images, make a third one which is a simple 
# composition of these 2

if flagThird != 0:
	band3 = normalize(img3)
	band3 = logarithmFilter(band3)
else:
	band3 = cv2.addWeighted(band1, 0.5, band2, 0.5, 0)

# change the images hue value according to their wavelenght:
# 	the lowest wavelenght gets the blue hue (120)
# 	the highest wavelenght gets the red hue (0)
# 	the mid value wavelenght gets the green hue (60)
#	if there is only 2 input images, the composed image gets the green hue (60)

if flagThird != 0:
	if wl1 > wl2 > wl3:
		img1_hue = 0
		img2_hue = 60
		img3_hue = 120
	elif wl1 > wl3 > wl2:
		img1_hue = 0
		img3_hue = 60
		img2_hue = 120
	elif wl2 > wl1 > wl3:
		img2_hue = 0
		img1_hue = 60
		img3_hue = 120
	elif wl2 > wl3 > wl1:
		img2_hue = 0
		img3_hue = 60
		img1_hue = 120
	elif wl3 > wl1 > wl2:
		img3_hue = 0
		img1_hue = 60
		img2_hue = 120
	elif wl3 > wl2 > wl1:
		img3_hue = 0
		img2_hue = 60
		img1_hue = 120
else:
	if wl1 > wl2:
		img1_hue = 0
		img3_hue = 60
		img2_hue = 120
	elif wl2 > wl1:
		img2_hue = 0
		img3_hue = 60
		img1_hue = 120

# the saturation value of the images is settled to 180, this way the colors
# aren't too vibrant (cause it would make the final image look more artificial)

# 1st image

img1_hsv = gray2hsv(band1)
h, s, v = cv2.split(img1_hsv)
s[:] = 180
h[:] = img1_hue
img1_hsv = cv2.merge((h, s, v))
img1_rgb = cv2.cvtColor(img1_hsv, cv2.COLOR_HSV2BGR)

# 2nd image

img2_hsv = gray2hsv(band2)
h, s, v = cv2.split(img2_hsv)
s[:] = 180
h[:] = img2_hue
img2_hsv = cv2.merge((h, s, v))
img2_rgb = cv2.cvtColor(img2_hsv, cv2.COLOR_HSV2BGR)

# 3rd image

img3_hsv = gray2hsv(band3)
h, s, v = cv2.split(img3_hsv)
s[:] = 180
h[:] = img3_hue
img3_hsv = cv2.merge((h, s, v))
img3_rgb = cv2.cvtColor(img3_hsv, cv2.COLOR_HSV2BGR)

# defining the parameters (weights of each image and the gamma correction) 
# for overlaying (> than 100% makes the image brighter, < than 100% makes
# the image more transparent, negative gamma value makes a darker image,
# positive gamma value makes a brighter image)

alpha1 = alpha2 = 1.5 	# 150%
beta1 = 0.5 			# 50%
beta2 = 2 				# 200%
gamma1 = -25
gamma2 = 0

# overlay the images following their wavelenght order:
#	lowest (blue) < mid (green) < highest (red)

if flagThird != 0:
	if wl1 < wl2 < wl3:
		result = cv2.addWeighted(img1_rgb, alpha1, img2_rgb, beta1, gamma1)
		result = cv2.addWeighted(result, alpha2, img3_rgb, beta2, gamma2)
	elif wl1 < wl3 < wl2:
		result = cv2.addWeighted(img1_rgb, alpha1, img3_rgb, beta1, gamma1)
		result = cv2.addWeighted(result, alpha2, img2_rgb, beta2, gamma2)
	elif wl2 < wl1 < wl3:
		result = cv2.addWeighted(img2_rgb, alpha1, img1_rgb, beta1, gamma1)
		result = cv2.addWeighted(result, alpha2, img3_rgb, beta2, gamma2)
	elif wl2 < wl3 < wl1:
		result = cv2.addWeighted(img2_rgb, alpha1, img3_rgb, beta1, gamma1)
		result = cv2.addWeighted(result, alpha2, img1_rgb, beta2, gamma2)
	elif wl3 < wl1 < wl2:
		result = cv2.addWeighted(img3_rgb, alpha1, img1_rgb, beta1, gamma1)
		result = cv2.addWeighted(result, alpha2, img2_rgb, beta2, gamma2)
	elif wl3 < wl2 < wl1:
		result = cv2.addWeighted(img3_rgb, alpha1, img2_rgb, beta1, gamma1)
		result = cv2.addWeighted(result, alpha2, img1_rgb, beta2, gamma2)
else:
	beta1 = 1 # changes the weight for the composed image
	if wl1 < wl2:
		result = cv2.addWeighted(img1_rgb, alpha1, img3_rgb, beta1, gamma1)
		result = cv2.addWeighted(result, alpha2, img2_rgb, beta2, gamma2)
	elif wl2 < wl1:
		result = cv2.addWeighted(img2_rgb, alpha1, img3_rgb, beta1, gamma1)
		result = cv2.addWeighted(result, alpha2, img1_rgb, beta2, gamma2)

# shows the processed picture

cv2.imshow("Final picture", result)

# saves the picture as a PNG file if the user chose to

if flagSave == "y":
	cv2.imwrite(finalName + ".png", result)

cv2.waitKey(0)
cv2.destroyAllWindows()