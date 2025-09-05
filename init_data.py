#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import ProjectConfig, Channel, Schedule

def create_sample_data():
    project, created = ProjectConfig.objects.get_or_create(
        name="Demo Project",
        defaults={'timezone': 'Europe/Kiev', 'is_active': True}
    )
    
    if created:
        print("Created demo project")
    else:
        print("Demo project already exists")
    
    channels_data = [
        {'type': 'call', 'label': 'Позвонить', 'link': 'tel:+380123456789', 
         'priority': 1, 'show_in_top': True, 'is_active': True, 'icon': '📞'},
        {'type': 'callback', 'label': 'Заказать звонок', 'priority': 2, 
         'show_in_top': True, 'is_active': True, 'icon': '⏰'},
        {'type': 'messenger', 'label': 'Telegram', 'link': 'https://t.me/your_bot', 
         'priority': 3, 'show_in_top': False, 'is_active': True, 'icon': '💬'},
        {'type': 'messenger', 'label': 'WhatsApp', 'link': 'https://wa.me/380123456789', 
         'priority': 4, 'show_in_top': False, 'is_active': True, 'icon': '📱'},
        {'type': 'chat', 'label': 'Онлайн чат', 'priority': 5, 
         'show_in_top': False, 'is_active': True, 'icon': '💭'},
        {'type': 'form', 'label': 'Оставить заявку', 'priority': 6, 
         'show_in_top': False, 'is_active': True, 'icon': '📝'}
    ]
    
    for channel_data in channels_data:
        Channel.objects.get_or_create(
            project=project, type=channel_data['type'], label=channel_data['label'],
            defaults=channel_data
        )
    
    schedule_data = [
        {'day': 'monday', 'start_time': '09:00', 'end_time': '18:00', 'is_working_day': True},
        {'day': 'tuesday', 'start_time': '09:00', 'end_time': '18:00', 'is_working_day': True},
        {'day': 'wednesday', 'start_time': '09:00', 'end_time': '18:00', 'is_working_day': True},
        {'day': 'thursday', 'start_time': '09:00', 'end_time': '18:00', 'is_working_day': True},
        {'day': 'friday', 'start_time': '09:00', 'end_time': '18:00', 'is_working_day': True},
        {'day': 'saturday', 'start_time': '10:00', 'end_time': '16:00', 'is_working_day': True},
        {'day': 'sunday', 'start_time': '10:00', 'end_time': '16:00', 'is_working_day': False},
    ]
    
    for schedule_item in schedule_data:
        Schedule.objects.get_or_create(
            project=project, day=schedule_item['day'], defaults=schedule_item
        )
    
    print(f"\nSample data initialized! Project ID: {project.id}")

if __name__ == '__main__':
    create_sample_data()