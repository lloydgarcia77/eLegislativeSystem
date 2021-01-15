from django import template
# https://docs.djangoproject.com/en/3.1/howto/custom-template-tags/


register = template.Library()


@register.simple_tag 
def custom_data_format(date):  
    new_date = date.strftime("%b. %d, %Y, %I:%M %p")
    return new_date