import jinja2
import settings

environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(settings.TEMPLATE_DIR),
	autoescape=True)

def render_to_string(filename, context={}):
	template = environment.get_or_select_template(filename)
	return template.render(context)
