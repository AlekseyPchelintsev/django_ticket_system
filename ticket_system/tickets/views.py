from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from django.contrib.auth.decorators import login_required
from .models import Ticket, Message
from .forms import TicketForm, TicketStatusForm
from django.db.models import Count, Q

@login_required
def ticket_list(request):
    if request.user.role == 'admin':
        tickets = Ticket.objects.filter(status='open').annotate(
            new_messages=Count('messages', filter=Q(messages__is_read=False))
        ).order_by('-updated_at')  # Сортировка по обновлению
    else:
        tickets = Ticket.objects.filter(owner=request.user, status='open').annotate(
            new_messages=Count('messages', filter=Q(messages__is_read=False))
        ).order_by('-updated_at')  # Сортировка по обновлению

    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.owner = request.user
            ticket.save()
            return redirect('ticket_list')
    else:
        form = TicketForm()
    return render(request, 'tickets/ticket_form.html', {'form': form})

@login_required
def ticket_update(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, owner=request.user)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('ticket_list')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'tickets/ticket_form.html', {'form': form})

@login_required
def change_ticket_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.user.is_superuser:
        ticket.status = 'closed' if ticket.status == 'open' else 'open'
        ticket.save()
    redirect_to = request.GET.get('redirect_to', 'ticket_list')
    return redirect(redirect_to)

@login_required
def delete_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    
    if request.method == 'POST':
        ticket.delete()
        return redirect('ticket_list')  # Перенаправляем на страницу со списком тикетов
    
    return render(request, 'tickets/delete_ticket_confirm.html', {'ticket': ticket})


@csrf_exempt
def send_message(request, ticket_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content')

            # Получите тикет по ID
            ticket = Ticket.objects.get(id=ticket_id)

            # Создайте новое сообщение
            message = Message.objects.create(
                ticket=ticket,
                user=request.user,  # Предполагается, что пользователь аутентифицирован
                content=content,
                created_at=timezone.now()
            )

            return JsonResponse({
                'success': True,
                'user': message.user.get_full_name(),
                'content': message.content,
                'created_at': message.created_at.strftime("%d.%m.%Y %H:%M"),
            })
        except Ticket.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ticket not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def mark_as_read(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        # Обновляем все непрочитанные сообщения как прочитанные
        ticket.messages.filter(is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@login_required
def ticket_closed(request):
    if request.user.role == 'admin':
        tickets = Ticket.objects.filter(status='closed').annotate(
            new_messages=Count('messages', filter=Q(messages__is_read=False))
        ).order_by('-closed_at')  # Сначала недавно закрытые тикеты
    else:
        tickets = Ticket.objects.filter(owner=request.user, status='closed').annotate(
            new_messages=Count('messages', filter=Q(messages__is_read=False))
        ).order_by('-closed_at')  # Сначала недавно закрытые тикеты

    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})