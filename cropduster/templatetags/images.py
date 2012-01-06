from coffin import template
from coffin.template.loader import get_template
register = template.Library()
from django.conf import settings
from cropduster.models import Size
import os

image_sizes = Size.objects.all()
image_size_map = {}
for size in image_sizes:
	image_size_map[(size.size_set_id, size.slug)] = size


@register.object
def get_image(image, size_name="large", template_name="image.html", width=None, height=None, crop_on_request=False, **kwargs):

	if image:
		
		try:
			image_size = image_size_map[(image.size_set_id, size_name)]
		except KeyError:
			return ""
		
		
		# Check if the file doesnt exist and its set to crop on request
		if crop_on_request and image_size.crop_on_request and not os.path.exists(image.thumbnail_path(image_size)):
			import ipdb;ipdb.set_trace()
			image.create_thumbnail(size_name)
			
		image_url = image.thumbnail_url(size_name)
		if image_url is None or image_url == "":
			return ""
		
	
		kwargs["image_url"] = image_url			
		kwargs["width"] = width or image_size.width or ""
		kwargs["height"] = height or image_size.height  or ""
		

		if hasattr(settings, "CROPDUSTER_KITTY_MODE") and settings.CROPDUSTER_KITTY_MODE:
			kwargs["image_url"] = "http://placekitten.com/{0}/{1}".format(kwargs["width"], kwargs["height"])

		kwargs["size_name"] = size_name
		kwargs["attribution"] = image.attribution
		kwargs["alt"] = kwargs["alt"] if "alt" in kwargs else image.caption
		kwargs["title"] = kwargs["title"] if "title" in kwargs else kwargs["alt"]
			


		tpl = get_template("templatetags/" + template_name)
		ctx = template.Context(kwargs)
		return tpl.render(ctx)
	else:
		return ""

	
		
		