#/usr/bin/env python
# -*- encoding:utf8 -*-
from django.conf import settings
from django.http import HttpResponse
from StringIO import StringIO
import random, os
import Image, ImageFont,ImageDraw

def index(request):
	#Load a random font
	fontslocation = settings.STATICFILES_DIRS[0] + "/fonts/captcha/"
	fonts = os.listdir(fontslocation)
	font = ImageFont.truetype(fontslocation + random.choice(fonts),25)

	#Create the image with  400x50 size
	image = Image.new("RGBA",(90,40),(255,255,255,0))
	draw = ImageDraw.Draw(image)

	#Draw the txt we get from getBasicMath
	draw.text((0,0),getBasicMath(request),font=font,fill="#000000")

	#Create a StringIO that we can use to save the image
	data = StringIO()
	image.save(data,format="PNG")

	#Return the image directly from memory
	data.seek(0)
	return HttpResponse(data.read(),content_type="image/png")

def getBasicMath(request):
	# the 3 types of operators we'll support
	operator = random.choice(["+","-","x"])

	#If its multiplication, lets use samller numbers
	if (operator == "x"):
		num1 = random.randint(0,10)
		num2 = random.randint(0,10)
		#Store the coorect answer in session
		request.session['captcha_answer'] = num1 * num2
	else:
		num1 = random.randint(20,40)
		num2 = random.randint(0,20)

		#Store the correct answer in session
		if (operator == "+"):
			request.session['captcha_answer'] = num1 + num2
		else:
			request.session['captcha_answer'] = num1 - num2

	#This is our output
	return str(num1) + operator + str(num2) + "=";
