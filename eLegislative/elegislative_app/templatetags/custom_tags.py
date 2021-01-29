from django import template
# https://docs.djangoproject.com/en/3.1/howto/custom-template-tags/


register = template.Library()


@register.simple_tag 
def custom_data_format(date):  
    new_date = date.strftime("%b. %d, %Y, %I:%M %p")
    return new_date

@register.simple_tag 
def custom_date_format_simple(date):
    new_date = date.strftime("%m/%d/%Y")
    return new_date

@register.filter
def model_name(value):
    value = value.__class__.__name__
    return value


@register.simple_tag 
def compute_percentage(*args):
    if args is None:
        return False
    x = args[0] 
    y = 0

    # for a in list(args)[1:]:
    for a in list(args): 
        y += a
    
    # (5 / 30) * 100
    #  
    
    if x != 0 and y != 0:
        total = (x / y) * 100
    else:
        total = 0
    
    return round(total,2)


 