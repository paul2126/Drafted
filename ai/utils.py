from .views import RecommendEventsView
def recommend_events(question_id: int, request):
    view = RecommendEventsView()
    return view.get(request, question_id)
