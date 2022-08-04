from django.utils.timezone import now
from django.db import models
from django.conf import settings


class Instructor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_time = models.BooleanField(default=True)  # type: ignore
    total_learners = models.IntegerField()

    objects = models.Manager()

    def __str__(self):
        return self.user.username  # type: ignore


class Learner(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    STUDENT = "student"
    DEVELOPER = "developer"
    DATA_SCIENTIST = "data_scientist"
    DATABASE_ADMIN = "dba"
    OCCUPATION_CHOICES = [
        (STUDENT, "Student"),
        (DEVELOPER, "Developer"),
        (DATA_SCIENTIST, "Data Scientist"),
        (DATABASE_ADMIN, "Database Admin"),
    ]
    occupation = models.CharField(
        null=False, max_length=20, choices=OCCUPATION_CHOICES, default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    objects = models.Manager()

    def __str__(self):
        return f"{self.user.username}, {self.occupation}"


class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default="online course")
    image = models.ImageField(upload_to="course_images/")
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Enrollment")
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    objects = models.Manager()

    def __str__(self):
        return f"{self.name=}, {self.description=}"


class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

    objects = models.Manager()


class Enrollment(models.Model):
    AUDIT = "audit"
    HONOR = "honor"
    BETA = "BETA"
    COURSE_MODES = [(AUDIT, "Audit"), (HONOR, "Honor"), (BETA, "BETA")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)  # type: ignore

    objects = models.Manager()

    def __str__(self):
        return f"{self.user.username} | {self.course.name} | {self.date_enrolled}"


class Question(models.Model):
    question_text = models.TextField()
    grade = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return f"{self.question_text} | {self.course.name}"


class Choice(models.Model):
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return f"Q : {self.question_id.question_text} | choice : {self.choice_text} "


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)

    objects = models.Manager()

    def __str__(self):
        return f"{self.enrollment.user.username} Enrolled in : {self.enrollment.course.name}"
