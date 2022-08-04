from onlinecourse.models import Choice, Course, Question


def get_course_questions(c: int | Choice):
    if isinstance(c, int):
        c = Course.objects.get(id=c)
    questions = Question.objects.filter(course=c)
    c_questions = []
    for question in questions:
        c_questions.append(
            {
                "question": question,
                "choices": Choice.objects.filter(question_id=question),
            }
        )
    return c_questions
