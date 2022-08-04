from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
import logging

from onlinecourse.utils import get_course_questions

from .models import Choice, Course, Enrollment, Question, Submission

logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, "onlinecourse/user_registration_bootstrap.html", context)
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["psw"]
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context["message"] = "User already exists."
            return render(
                request, "onlinecourse/user_registration_bootstrap.html", context
            )


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["psw"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context["message"] = "Invalid username or password."
            return render(request, "onlinecourse/user_login_bootstrap.html", context)
    else:
        return render(request, "onlinecourse/user_login_bootstrap.html", context)


def logout_request(request):
    logout(request)
    return redirect("onlinecourse:index")


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = "onlinecourse/course_list_bootstrap.html"
    context_object_name = "course_list"

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by("-total_enrollment")[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.View):
    template_name = "onlinecourse/course_detail_bootstrap.html"

    def get(self, request, pk):
        c = Course.objects.get(id=pk)
        c_questions = get_course_questions(c)
        context = {"course": c, "questions": c_questions}
        return render(request, template_name=self.template_name, context=context)


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        Enrollment.objects.create(user=user, course=course, mode="honor")
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(
        reverse(viewname="onlinecourse:course_details", args=(course.id,))
    )


def submit(request, course_id):
    def extract_answers():
        submitted_anwsers = []
        for key in request.POST:
            if key.startswith("choice"):
                choice_id = int(str(key).replace("choice_", ""))
                choice = Choice.objects.get(id=choice_id)
                submitted_anwsers.append(choice)
        return submitted_anwsers

    course = Course.objects.get(id=course_id)
    user = User.objects.get(username=request.user.username)
    if request.method == "POST":
        try:
            enrollment = Enrollment.objects.get(user=user, course=course)
            choices = extract_answers()
            Submission.objects.create(enrollment=enrollment)
            s = Submission.objects.get(enrollment=enrollment)
            s.choices.set(choices)
            s.save()
            return HttpResponseRedirect(
                reverse(
                    "onlinecourse:show_exam_result",
                    args=(
                        course.id,
                        s.id,
                    ),
                )
            )
        except Exception as e:
            logging.error(f"An error occured while submitting results :: {e}")
    return HttpResponseRedirect(
        reverse("onlinecourse:course_details", args=(course.id,))
    )


def show_exam_result(request, course_id, submission_id):
    if Submission.objects.filter().count() == 0:
        return HttpResponseRedirect(
            reverse("onlinecourse:course_details", args=(course_id,))
        )
    submission = Submission.objects.get(id=submission_id)
    course = Course.objects.get(id=course_id)
    # a slow algorithm... But it works fine
    c_questions = get_course_questions(course)
    for choice in submission.choices.all():
        for idx, q in enumerate(c_questions):
            if q["question"].id == choice.question_id.id:
                if not "chosen_answers" in c_questions[idx]:
                    c_questions[idx]["chosen_answers"] = []
                c_questions[idx]["chosen_answers"].append(choice)
                # append the correct answers if they don't exist yet
                if not "correct_answers" in c_questions[idx]:
                    c_questions[idx]["correct_answers"] = [
                        ch
                        for ch in Choice.objects.filter(
                            is_correct=True, question_id=c_questions[idx]["question"]
                        )
                    ]

    correctly_chosen_questions = [
        each.question_id
        for each in filter(lambda x: x.is_correct, submission.choices.all())
    ]
    total_score = sum(
        map(lambda x: x.grade, Question.objects.filter(course__id=course_id))
    )
    attained_score = sum(map(lambda x: x.grade, correctly_chosen_questions))

    context = {
        "course": course,
        "questions": c_questions,
        "grade": int((attained_score / total_score) * 100),
        "total_score": int((total_score / total_score) * 100),
    }
    return render(request, "onlinecourse/exam_result_bootstrap.html", context)
