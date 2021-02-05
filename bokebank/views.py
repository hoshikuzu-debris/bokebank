from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .models import Department, User, Question, Answer

class Index(ListView):
    template_name = 'bokebank/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.order_by('-asked_date')


class AnswerCreate(LoginRequiredMixin, CreateView):

    model = Answer
    template_name = 'bokebank/answer.html'
    # fields = ['question', 'text']
    fields = ['text']
    asked_question = Question.objects.get(id=5)

    def form_valid(self, form):
        form.instance.panelist = self.request.user
        form.instance.question = self.asked_question
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('bokebank:index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = self.asked_question
        return context    


def main(request):
    return HttpResponse("You're looking at main.")

class CheckList(ListView):
    template_name = 'bokebank/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.order_by('asked_date')

class Check(UpdateView):
    model = Question
    template_name = 'bokebank/check.html'


def evaluate(request, pk):
    question = get_object_or_404(Question, pk=pk)

    try:
        selected_answer = question.answer_set.get(pk=request.POST['answer'])
    except (KeyError, Answer.DoesNotExist):
        return render(request, 'bokebank/check.html',{
            'question': question,
            'error_message': "You didn't select an answer.",
        })
    else:
        selected_answer.evaluate(1)
        return HttpResponseRedirect(reverse('bokebank:detail', args=(question.id,)))

class Gallery(ListView):
    template_name = 'bokebank/gallery.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.order_by('-asked_date')

class Detail(DetailView):
    model = Question
    template_name = 'bokebank/detail.html'

def userpage(request, username):
    return HttpResponse(f"You're looking at { username }.")