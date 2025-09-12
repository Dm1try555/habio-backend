#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import ProjectConfig, Channel, Schedule, Lead, ChatSession, ChatMessage

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
    
    # Demo leads
    try:
        default_channel = Channel.objects.filter(project=project).first()
        if default_channel:
            Lead.objects.get_or_create(
                project=project,
                channel=default_channel,
                contact='John Doe <john@example.com>',
                defaults={
                    'message': 'Хочу подключить онлайн-чат на сайт. Телефон: +1 555 123 4567',
                    'utm_source': 'demo',
                    'utm_medium': 'seed',
                    'utm_campaign': 'init_data',
                    'page_url': 'https://example.com/',
                    'client_id': 'demo-client-1',
                    'device_type': 'desktop',
                    'language': 'en',
                    'processed': False,
                }
            )
            Lead.objects.get_or_create(
                project=project,
                channel=default_channel,
                contact='Jane Smith <jane@example.com>',
                defaults={
                    'message': 'Интересуют тарифы и интеграции. Телефон: +1 555 765 4321',
                    'utm_source': 'demo',
                    'utm_medium': 'seed',
                    'utm_campaign': 'init_data',
                    'page_url': 'https://example.com/pricing',
                    'client_id': 'demo-client-2',
                    'device_type': 'mobile',
                    'language': 'en',
                    'processed': True,
                }
            )
    except Exception as e:
        print(f"Failed to create demo leads: {e}")

    # Demo chat session and messages
    try:
        session, _ = ChatSession.objects.get_or_create(
            project=project,
            client_id='demo-chat-client',
            defaults={'page_url': 'https://example.com/', 'is_active': True}
        )
        if not session.messages.exists():
            ChatMessage.objects.create(session=session, message_type='user', content='Здравствуйте! Подскажите по установке виджета?')
            ChatMessage.objects.create(session=session, message_type='admin', content='Здравствуйте! Да, конечно, помогу. У вас Nuxt или другой фреймворк?')
            ChatMessage.objects.create(session=session, message_type='user', content='Nuxt 3.')
            ChatMessage.objects.create(session=session, message_type='admin', content='Отлично. Я вышлю инструкцию и помогу с интеграцией.')
    except Exception as e:
        print(f"Failed to create demo chat: {e}")

    print(f"\nSample data initialized! Project ID: {project.id}")

if __name__ == '__main__':
    create_sample_data()