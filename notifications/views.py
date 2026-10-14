from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification, Announcement


@login_required
def notification_list_view(request):
    """View all notifications for the user."""
    notifications = Notification.objects.filter(user=request.user)
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')[:5]

    context = {
        'page_title': 'Notifications & Announcements',
        'notifications': notifications,
        'announcements': announcements,
    }
    return render(request, 'notifications/list.html', context)


@login_required
def mark_notification_read_view(request, pk):
    """Mark a single notification as read."""
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})

    if notif.link:
        return redirect(notif.link)
    return redirect('notification_list')


@login_required
def mark_all_read_view(request):
    """Mark all notifications for the current user as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})

    return redirect('notification_list')
