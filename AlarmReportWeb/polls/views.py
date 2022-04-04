from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Question

# Create your views here.
def index(request):
    lastestQuestionList = Question.objects.order_by('-pub_date')[:5]
    # output = ' ,'.join([q.question_text for q in lastestQuestionList])
    # template = loader.get_template('polls/index.html')
    context = {
        'lastestQuestionList': lastestQuestionList
    }
    # return HttpResponse(template.render(context, request))
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    # return HttpResponse("You are lookinh at question %s." % question_id)
    question = get_object_or_404(Question, pk=question_id)
    context = {'question': question}
    return render(request, 'polls/detail.html', context)

def results(request, question_id):
    # response = "You're looking at the result of question %s."
    # return HttpResponse(response % question_id)
    question = Question.objects.get(pk=question_id)
    context = {'question': question}
    return render(request, 'polls/result.html', context)

def vote(request, question_id):
    return HttpResponse("You're voting for question %s." % question_id)