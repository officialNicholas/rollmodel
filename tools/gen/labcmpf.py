import sys
from PIL import Image
a=Image.open(sys.argv[1]); W=1536/4.6
row=a.crop((0,int(1024*0.44),int(4*W),int(1024*0.74)))
ref=Image.open('lab/ref/expr.png'); ref=ref.resize((int(ref.width*row.height/ref.height),row.height))
c=Image.new('RGB',(max(row.width,ref.width),row.height*2)); c.paste(ref,(0,0)); c.paste(row,(0,row.height)); c.save(sys.argv[2])
