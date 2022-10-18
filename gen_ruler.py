import math, sys, argparse
from PIL import Image, ImageDraw, ImageFont

NM_IN_FEET = 6076.12

# parameters of the WGS 84 geoid 
WGS_A = 6378137.0
WGS_F = 1.0/298.257223563
WGS_B = WGS_A * (1.0 - WGS_F)
WGS_E2 = 6.69437999014E-3

def r2d(r):
	return r/math.pi*180.0;

def d2r(d):
	return d/180.0*math.pi;

def scale_for_latitude(latitude): 
	return math.cos(d2r(latitude))

def geodetic_lat_to_geocentric(latitude):
	# https://proj.org/operations/conversions/geoc.html
	return r2d(math.atan((1.0 - WGS_E2)*math.tan(d2r(latitude))))

def draw_flip(image, x, y, text, font, fill, a):
	imageDraw = ImageDraw.Draw(image)
	tw, th = imageDraw.textsize(text, font)
	rim = Image.new("RGBA", (tw, th))
	rimDraw = ImageDraw.Draw(rim)
	rimDraw.text((0, 0), text, font=font, fill=fill)
	rim = rim.rotate(a, Image.Resampling.NEAREST, expand=1)
	image.paste(rim, (int(x), int(y)))

def create_ruler_image(scale, span, latitude_scale=1.0, DPI=144, height=1.0, title="", min_width=-1):
	lr_margin=int(0.3*DPI)
	tb_margin=int(0.25*DPI)
	bb_height = int(0.1*DPI)

	minute_inches = NM_IN_FEET * 12 / scale
	minute_dots = minute_inches * DPI * latitude_scale
	scale_dots = minute_dots*span

	scale_width = int(scale_dots)
	img_width = lr_margin*2 + scale_width + 1 
	img_height = int(height*DPI)
	

	# scale a parameter for a given DPI 
	def psi(s, minv=-sys.maxsize, maxv=sys.maxsize):
		return min(max(int(s * float(DPI)/144.0 + 0.5), minv), maxv)

	img = Image.new("RGBA", (img_width if min_width < 0 else max(min_width, img_width), img_height))
	draw = ImageDraw.Draw(img)
	
	scale_img = Image.new("RGBA", (img_height, lr_margin))
	s_draw = ImageDraw.Draw(scale_img)
	fnt = ImageFont.truetype("Impact", psi(18))
	msg = "1:{:,}".format(scale)
	tw, th = draw.textsize(msg, fnt)
	s_draw.text((img_height/2 - tw/2, lr_margin/2 - th/2), msg, font=fnt, fill=(0, 0, 0, 255))
	scale_img = scale_img.rotate(90, Image.Resampling.NEAREST, expand=1)
	img.paste(scale_img)

	scale_img = Image.new("RGBA", (img_height, lr_margin))
	s_draw = ImageDraw.Draw(scale_img)
	fnt = ImageFont.truetype("Impact", psi(18))
	msg = title
	tw, th = draw.textsize(msg, fnt)
	s_draw.text((img_height/2 - tw/2, lr_margin/2 - th/2), msg, font=fnt, fill=(0, 0, 0, 255))
	scale_img = scale_img.rotate(90, Image.Resampling.NEAREST, expand=1)
	img.paste(scale_img, (img_width - lr_margin, 0))


	def xywh(x, y, w, h):
		return (x, y, x+w, y+h)

	def draw_bw_bar(y, h, divs=1):
		for i in range(span*divs):
			if i%2 == 0:
				draw.rectangle(xywh(lr_margin + int(minute_dots*i/divs+0.5), y, int(minute_dots/divs), h), fill=(0, 0, 0, 255))
		#outline bottom bar
		draw.rectangle(xywh(lr_margin, y, scale_width, h), outline=(0, 0, 0, 255))			
	
	def draw_ticks(y, h, divs=1, w=1, labels=[], fs=16, a=0):
		for i in range(1, divs):
			draw.line(xywh(lr_margin + int((scale_dots/divs)*i +0.5) , y, 0, -h),  fill=(0, 0, 0, 255), width=w)
		
		draw.line(xywh(lr_margin + int(w/2), y, 0, -h),  fill=(0, 0, 0, 255), width=w)
		draw.line(xywh(lr_margin + scale_width - int(w/2 - 1), y, 0, -h),  fill=(0, 0, 0, 255), width=w)
		
		fnt = ImageFont.truetype("Helvetica", psi(fs))
		if len(labels):
			for i, l in enumerate(labels):
				tw, th = draw.textsize(l, fnt)
				ty = y - h
				ty -= ((th + psi(5) ) if h > 0 else -psi(5))  
				draw_flip(img, lr_margin + (scale_dots/divs)*i - (tw/2), ty, l, fnt, (0, 0, 0, 255), a)
		
	draw_bw_bar(img_height/2-bb_height, bb_height, 10)			
	draw_ticks(img_height/2+bb_height, -(bb_height*0.25), span*2, psi(1,1))
	
	draw.line(xywh(lr_margin-(bb_height/5), img_height/2, bb_height/5, 0),  fill=(0, 0, 0, 255), width=psi(1,1))
	draw.line(xywh(lr_margin+scale_width, img_height/2, bb_height/5, 0),  fill=(0, 0, 0, 255), width=psi(1,1))

	draw_bw_bar(img_height/2, bb_height)
	
	draw_ticks(0, -(bb_height*2), span, psi(2,1), [str(i) for i in range(span+1)], 20)
	draw_ticks(0, -(bb_height*1.5), span*2, psi(1,1), ['', '.5'] * span + [''])
	draw_ticks(0, -(bb_height*1), span*10, psi(1,1))
	if scale < 100000:
		draw_ticks(0, -(bb_height*0.5), span*20, psi(0.5,1))
		draw_ticks(0, -(bb_height*0.3), span*40, psi(0.5,1))

	draw_ticks(img_height, (bb_height*2), span, psi(2,1), [str(i) for i in range(span+1)], 20, a=180)
	draw_ticks(img_height, (bb_height*1.5), span*2, psi(1,1), ['', '.5'] * span + [''], a=180)
	draw_ticks(img_height, (bb_height*1), span*10, psi(1,1), a=180)
	if scale < 100000:
		draw_ticks(img_height, (bb_height*0.5), span*20, psi(0.5,1), a=180)
		draw_ticks(img_height, (bb_height*0.3), span*40, psi(0.5,1), a=180)

	return img

def lat_from_deg_min(d, m):
	return d + m/60.0  

#argparse.ArgumentParser(description='Process some integers.')
parser = argparse.ArgumentParser()
parser.add_argument('scale', type=int, help='Scale of chart ruler (integer N for scale of 1 to N)')
parser.add_argument('latitude', type=str, help='Latitude at which to generate the longitude ruler (in degrees and minutes)')
parser.add_argument('length', type=int, help='Length of the ruler, in minutes of latitude / longitude')

parser.add_argument('--dpi', type=int, default=144, help='DPI of resulting image')


args = parser.parse_args()
lat_deg, lat_min = [float(v) for v in args.latitude.split(" ")]
 
print("Generating ruler images for scale 1:{} at latitude {}".format(args.latitude, args.latitude))

r = create_ruler_image(args.scale, args.length, 1.0, DPI=args.dpi, title="Distance/Latitude")
r.save("distance_{}_{}.png".format(args.scale, args.length), "PNG", dpi=(args.dpi, args.dpi))

lat_scale = scale_for_latitude(geodetic_lat_to_geocentric(lat_from_deg_min(lat_deg, lat_min)))
t = "Longitude @ {}° {}'".format(int(lat_deg), int(lat_min))

r = create_ruler_image(args.scale, args.length, lat_scale, DPI=args.dpi, title=t, min_width = r.size[0])
r.save("longitude_{}_{}_{}_{}.png".format(args.scale, int(lat_deg), int(lat_min), args.length), "PNG", dpi=(args.dpi, args.dpi))


