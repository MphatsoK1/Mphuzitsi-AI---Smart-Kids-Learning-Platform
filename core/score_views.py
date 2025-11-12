from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required  # Optional, if you want to require login
import json
from django.shortcuts import render
from .models import GameScore  # Adjust import based on your app structure

@csrf_protect
@login_required  # Uncomment if you want to require user login
def save_score(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            score_entry = GameScore(
                user=request.user if request.user.is_authenticated else None,
                game_name=data.get('game_name', 'Unknown'),
                score=data.get('score', 0),
                milestone=data.get('milestone', '')
            )
            score_entry.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'method_not_allowed': True}, status=405)

def scores(request):
    # Optionally require login: @login_required
    user_scores = GameScore.objects.filter(user=request.user) if request.user.is_authenticated else GameScore.objects.none()
    user_scores = user_scores.order_by('-timestamp')  # Most recent first
    return render(request, 'scores.html', {'scores': user_scores})