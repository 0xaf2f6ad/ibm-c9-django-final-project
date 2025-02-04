from django.contrib import admin

from .models import (
    Choice,
    Course,
    Enrollment,
    Lesson,
    Instructor,
    Learner,
    Question,
    Submission,
)


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 4


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 4


class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ("name", "pub_date")
    list_filter = ["pub_date"]
    search_fields = ["name", "description"]


class LessonAdmin(admin.ModelAdmin):
    list_display = ["title"]


admin.site.register(Instructor)
admin.site.register(Learner)

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)

admin.site.register(Question)
admin.site.register(Choice)

admin.site.register(Submission)
admin.site.register(Enrollment)
