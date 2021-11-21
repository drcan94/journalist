from django import template
from journalApp.models import Notification, RequestAuthorShip
from accounts.models import UserProfile
from django.utils import timezone
import json
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag("journalApp/show_notifications.html", takes_context=True)
def show_notifications(context):
    request_user = context["request"].user

    if request_user.is_authenticated:
        
        count = UserProfile.get_notification_count(self=context["request"])
        
        notifications = []
        
        types = [1, 2, 3, 4, 5, 6]

        for i in Notification.objects.all():
        
            if i.notification_type in types:
        
                if (i.notification_type == 5 or i.notification_type == 6) and i.from_user == request_user and i.is_seen == False:
                    notifications.append(i)
        
                if (i.notification_type != 5 and i.notification_type != 6) and i.to_user == request_user and i.is_seen == False:
                    notifications.append(i)

        time = timezone.now().time
        
        return {"notifications": notifications, "time": time, "count": count}

    else:
        return {}



def generate_paragraph(data):
    text = data.get('text').replace('&nbsp;', ' ')
    alignment = data.get('alignment')
    return f'<div class="ce-block"><div class="ce-block__content"><div class="ce-paragraph text-{alignment} cdx-block" contenteditable="false" data-placeholder="">{text}</div></div></div>'

def generate_list(data):
    list_li = ''.join([f'<li class="cdx-list__item">{item}</li>' for item in data.get('items')])
    tag = 'ol' if data.get('style') == 'ordered' else 'ul'
    return f'<div class="ce-block"><div class="ce-block__content"><{tag} class="cdx-block cdx-list cdx-list--{data.get("style")}" contenteditable="false">{list_li}</{tag}></div></div>'


def generate_checklist(data):
    text_list = ''
    for item in data.get('items'):
        if item["checked"] == True:
            text_list += f'<div class="cdx-checklist__item cdx-checklist__item--checked"><span class="cdx-checklist__item-checkbox"></span><div class="cdx-checklist__item-text" contenteditable="false">{item["text"]}</div></div>'
        else:
            text_list += f'<div class="cdx-checklist__item"><span class="cdx-checklist__item-checkbox"></span><div class="cdx-checklist__item-text" contenteditable="false">{item["text"]}</div></div>'
    return f'<div class="ce-block ce-block--focused"><div class="ce-block__content"><div class="cdx-block cdx-checklist">{text_list}</div></div></div>'


def generate_header(data):
    text = data.get('text').replace('&nbsp;', ' ')
    level = data.get('level')
    return f'<div class="ce-block"><div class="ce-block__content"><h{level} class="ce-header" contenteditable="false">{text}</h{level}></div></div>'


def generate_image(data):
    url = data.get('file', {}).get('url')
    caption = data.get('caption')
    return f'<div class="ce-block"><div class="ce-block__content"><div class="cdx-block image-tool image-tool--filled"><div class="image-tool__image" wfd-invisible="true"><div class="image-tool__image-preloader" style=""></div><img src="{url}" class="image-tool__image-picture"/></div><div class="cdx-input image-tool__caption" contenteditable="false" data-placeholder="Caption" wfd-invisible="true">{caption}</div></div></div></div>'


def generate_delimiter():
    return '<div class="ce-block"><div class="ce-block__content"><div class="ce-delimiter cdx-block"></div></div></div>'


def generate_table(data):
    rows = data.get('content', [])
    table = '<table>'
    table += '<thead>'
    for index, row in enumerate(rows):
        if index == 0:
            table += '<tr>'
            for cell in row:
                table += f'<th>{cell}</th>'
            table += '</tr>'

    table += '</thead>'

    table += '<tbody>'

    for index, row in enumerate(rows):
        if index != 0:
            table += '<tr>'
            for cell in row:
                table += f'<td>{cell}</td>'
            table += '</tr>'

    table += '</tbody>'
    table += '</table>'
    return f'<table>{table}</table>'


def generate_warning(data):
    title, message = data.get('title'), data.get('message')

    if title:
        title = f'<div class="alert__title">{title}</div>'
    if message:
        message = f'<div class="alert__message">{message}</div>'

    return f'<div class="ce-block"><div class="ce-block__content"><div class="cdx-block cdx-warning"><div class="cdx-input cdx-warning__title" contenteditable="false"><b>{title}</b></div><div class="cdx-input cdx-warning__message" contenteditable="false">{message}</div></div></div></div>'


def generate_quote(data):
    alignment = data.get('alignment')
    caption = data.get('caption')
    text = data.get('text')

    if caption:
        caption = f'<div class="cdx-input cdx-quote__caption" contenteditable="false">{caption}</div>'

    return f'<div class="ce-block"><div class="ce-block__content text-{alignment}"><blockquote class="cdx-block cdx-quote"><div class="cdx-input cdx-quote__text" contenteditable="false">{text}</div>{caption}</blockquote></div></div>'

                    

def generate_raw(data):
    return f'<div class="ce-block"><div class="ce-block__content"><div class="cdx-block ce-rawtool"><textarea readonly class="ce-rawtool__textarea cdx-input">{data.get("html")}</textarea></div></div></div>'





@register.filter(is_safe=True)
def editorjs(value):
    if not isinstance(value, dict):
        try:
            value = json.loads(value)
        except ValueError:
            return value
        except TypeError:
            return value

    html_list = []
    for item in value['blocks']:

        type, data = item.get('type'), item.get('data')

        if type == 'paragraph':
            html_list.append(generate_paragraph(data))
        elif type == 'Header':
            html_list.append(generate_header(data))
        elif type == 'List':
            html_list.append(generate_list(data))
        elif type == 'Checklist':
            html_list.append(generate_checklist(data))
        elif type == 'Image':
            html_list.append(generate_image(data))
        elif type == 'Delimiter':
            html_list.append(generate_delimiter())
        elif type == 'Warning':
            html_list.append(generate_warning(data))
        elif type == 'Table':
            html_list.append(generate_table(data))
        elif type == 'Raw':
            html_list.append(generate_raw(data))
        elif type == 'Quote':
            html_list.append(generate_quote(data))

    return mark_safe(''.join(html_list))
