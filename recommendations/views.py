from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Recommendation
from .services import RecommendationEngine


@login_required
def recommendation_list_view(request):
    """View generated recommendations for the student."""
    recommendations = RecommendationEngine.generate_recommendations_for_user(request.user)

    context = {
        'page_title': 'Smart Recommendations',
        'recommendations': recommendations,
    }
    return render(request, 'recommendations/list.html', context)


@login_required
def dismiss_recommendation_view(request, pk):
    """Dismiss a recommendation."""
    rec = get_object_or_404(Recommendation, pk=pk, student=request.user)
    rec.is_dismissed = True
    rec.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})

    return redirect('recommendation_list')
