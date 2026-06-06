from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from .models import Channel, Message
from django.conf import settings

User = get_user_model()

@login_required
def room_view(request, room_name):
    channel, _ = Channel.objects.get_or_create(name=room_name)
    messages = channel.messages.all().order_by('timestamp')[:50]
    

    users = User.objects.exclude(id=request.user.id)

    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'messages': messages,
        'users': users,
        'is_dm': False
    })

@login_required
def dm_view(request, username):
    other_user = get_object_or_404(User, username=username)
    
    ids = sorted([request.user.id, other_user.id])
    room_name = f"dm_{ids[0]}_{ids[1]}"
    
    channel, created = Channel.objects.get_or_create(name=room_name, is_private=True)
    if created:
        channel.members.add(request.user, other_user)

    messages = channel.messages.all().order_by('timestamp')[:50]
    users = User.objects.exclude(id=request.user.id)

    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'messages': messages,
        'users': users,
        'is_dm': True,
        'other_user': other_user
    })

@csrf_exempt
@login_required
def upload_image(request, room_name):
    if request.method == 'POST' and request.FILES.get('image'):
        channel, _ = Channel.objects.get_or_create(name=room_name)
        image_file = request.FILES['image']
        msg = Message.objects.create(sender=request.user, channel=channel, image=image_file, content="")
        return JsonResponse({'success': True, 'image_url': msg.image.url, 'username': request.user.username, 'message_id': msg.id})
    return JsonResponse({'success': False})

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@login_required
def upload_audio(request, room_name):
    if request.method == 'POST' and request.FILES.get('audio'):
        if request.user.is_blocked:
            return JsonResponse({'success': False})
        
        channel = get_object_or_404(Channel, name=room_name)
        audio_file = request.FILES['audio']
        
        msg = Message.objects.create(sender=request.user, channel=channel, content="[Wiadomość głosowa]")
        file_name = default_storage.save(f'audio/voice_{msg.id}.wav', ContentFile(audio_file.read()))
        
        return JsonResponse({'success': True, 'audio_url': settings.MEDIA_URL + file_name, 'message_id': msg.id})
    return JsonResponse({'success': False})

