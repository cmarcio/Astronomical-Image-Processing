""" 
	Astronomical Image Processing (DEMO VERSION)

	Group 16

	Marcio de Souza Campos 8937461
	Marly da Cruz Claudio  8936885
	Robson Marques Pessoa  8632563 

"""

from astropy.io import fits
import numpy as np
import cv2
import sys

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

flag = str(sys.argv[1])

if flag == "messier":
	img1 = fits.getdata("messier502.fits")
	img2 = fits.getdata("messier656.fits")
	img3 = fits.getdata("messier673.fits")
else:
	img1 = fits.getdata("eagle502.fits")
	img2 = fits.getdata("eagle656.fits")
	img3 = fits.getdata("eagle673.fits")

# pre-processing

band1 = normalize(img1)
band1 = logarithmFilter(band1)

band2 = normalize(img2)
band2 = logarithmFilter(band2)

band3 = normalize(img3)
band3 = logarithmFilter(band3)

# the saturation value of the images is settled to 180, this way the colors
# aren't too vibrant (cause it would make the final image look more artificial)

# 1st image has the lowest wavelenght, therefore it receives a blue hue (120)

img1_hsv = gray2hsv(band1)
h, s, v = cv2.split(img1_hsv)
s[:] = 180
h[:] = 120
img1_hsv = cv2.merge((h, s, v))
img1_rgb = cv2.cvtColor(img1_hsv, cv2.COLOR_HSV2BGR)

# 2nd image is in between the other wavelenght values, therefore it receives 
# a green hue (60)

img2_hsv = gray2hsv(band2)
h, s, v = cv2.split(img2_hsv)
s[:] = 180
h[:] = 60
img2_hsv = cv2.merge((h, s, v))
img2_rgb = cv2.cvtColor(img2_hsv, cv2.COLOR_HSV2BGR)

# 3rd image has the highest wavelenght, therefore it receives a red hue (0)

img3_hsv = gray2hsv(band3)
h, s, v = cv2.split(img3_hsv)
s[:] = 180
h[:] = 0
img3_hsv = cv2.merge((h, s, v))
img3_rgb = cv2.cvtColor(img3_hsv, cv2.COLOR_HSV2BGR)

# overlay the images and makes a gamma correction

result = cv2.addWeighted(img1_rgb, 1.5, img2_rgb, 0.5, -25)
result = cv2.addWeighted(result, 1.5, img3_rgb, 2, 0)

# shows the processed picture

cv2.imshow("Final picture", result)
cv2.waitKey(0)
cv2.destroyAllWindows()