from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Test, Page, Instruction
from .form_handlers import *
import string, random, hashlib

# Create your views here.

from collections import defaultdict

def hash_string(string, algorithm='sha256'):
    if algorithm == 'sha256':
        return hashlib.sha256(string.encode()).hexdigest()
    elif algorithm == 'md5':
        return hashlib.md5(string.encode()).hexdigest()
    else:
        raise ValueError('Unsupported algorithm')


def random_string(length=255):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))



def get_page_question_summary(page_id):
    page = Page.objects.filter(id=page_id).first()
    if not page:
        return None

    questions = Question.objects.filter(page=page).order_by("number")
    question_ids = questions.values_list("id", flat=True)

    # Preload related sub-questions and images
    sub_questions = SubQuestion.objects.filter(question_id__in=question_ids)
    images = Images.objects.filter(question_id__in=question_ids)

    # Build summary
    summary = []
    sub_map = defaultdict(list)
    image_map = defaultdict(list)

    for sub in sub_questions:
        sub_map[sub.question_id].append(sub)

    for img in images:
        image_map[img.question_id].append(img)

    indexOf = 0
    # for question in questions:
    #     q_id = question.id
    #     summary.append({
    #         "index": indexOf,
    #         "number": question.number,
    #         "sub_level": len(sub_map[q_id]),
    #         "image_count": len(image_map[q_id]),
    #     })
    #     indexOf += 1
    
    questions_count = questions.count()
    for x in range(0,3):
        if x <= (questions_count-1):
            question = questions[x]
            summary.append({
                "index": indexOf,
                "number": question.number,
                "active": "true",
                "sub_level": len(sub_map[question.id]),
                "image_count": len(image_map[question.id])
            })
        else:
            summary.append({
                "index": indexOf,
                "number": indexOf + 1,
                "active": "false",
                "sub_level": 0,
                "image_count": 0
            })
        indexOf += 1
    return summary


def index(request):
    template = loader.get_template("index.html")

    context = {

    }
    response = HttpResponse(template.render(context, request))
    return response


def dashboard(request):
    template = loader.get_template("dashboard.html")
    active_tests = Test.objects.filter(is_active=True)

    error_message = ""


    if request.method == "POST":
        form_data = request.POST
        test_id = form_data.get("test_id", None)
        password = form_data.get("password", None)
        if test_id and password:
            test = Test.objects.filter(id=int(test_id)).first()
            if test and hash_string(password, 'md5') == test.password:
                return HttpResponseRedirect(reverse("start_test_page", args=[test.id]))
            else: error_message = "Incorrect Password. Please Try Again."

    context = {
        "active_tests": active_tests,
        "error_message": error_message
    }
    response = HttpResponse(template.render(context, request))
    return response


# Take tests
def test_page(request, test_id, page_number):
    test = Test.objects.filter(id=test_id).first()
    show_next_button = show_previous_button = show_done_button = False
    if not test:
        return HttpResponse("Test not found")
    
    current_page = Page.objects.filter(test=test, page_number=page_number, is_active=True).first()
    questions = Question.objects.filter(page_id=current_page.id).order_by("number")
    question_ids = questions.values_list("id", flat=True)
    sub_questions = SubQuestion.objects.filter(question_id__in=question_ids).order_by("number")
    images = Images.objects.filter(question_id__in=question_ids)
    
    if not current_page:
        return HttpResponse("Page not found")
    total_pages = Page.objects.filter(test=test, is_active=True).count()
    total_time = test.timer_count * 60
    if Page.objects.filter(test=test, page_number__gt=page_number, is_active=True).exists():
        show_next_button = True
        next_page_number = Page.objects.filter(test=test, page_number__gt=page_number, is_active=True).order_by('page_number').first().page_number
    else:
        show_next_button = False
        show_done_button = True
    if Page.objects.filter(test=test, page_number__lt=page_number, is_active=True).exists():
        show_previous_button = True
        previous_page_number = Page.objects.filter(test=test, page_number__lt=page_number, is_active=True).order_by('-page_number').first().page_number
    else:
        show_previous_button = False
    print("per page: ", test.time_per_page)
    template = loader.get_template("test_page.html")
    context = {
        "questions": questions,
        "sub_questions": sub_questions,
        "images": images,
        "test": current_page.test,
        "page": current_page,
        "test_page": True,
        "show_next_button": show_next_button,
        "show_previous_button": show_previous_button,
        "next_page_number": next_page_number if show_next_button else None,
        "previous_page_number": previous_page_number if show_previous_button else None,
        "show_done_button": show_done_button,
        "total_pages": total_pages,
        "total_time": total_time
    }
    response = HttpResponse(template.render(context, request))
    response.set_cookie('test_id', test_id, max_age=3600, httponly=True, secure=False)
    response.set_cookie('page_id', current_page.id, max_age=3600, httponly=True, secure=False)
    response.set_cookie('page_done', 'false', max_age=3600, httponly=True, secure=False)
    response.set_cookie('is_started', 'True', max_age=3600, httponly=True, secure=False)
    return response


def test_page2(request, test_id):
    test = Test.objects.filter(id=test_id).first()
    if not test:
        return HttpResponse("Test not found")
    total_pages = Page.objects.filter(test=test).count()
    total_time = test.timer_count * 60
    time_per_page = test.time_per_page
    
    if request.method == "POST":
        form_data = request.POST
        previous_page_number = form_data.get("page_number", None)
        if not previous_page_number: print("page number is null")
        else:
            current_page_number = int(previous_page_number)
            current_page = Page.objects.filter(is_active=True, test=test, page_number__gt=previous_page_number).order_by("page_number").first()
            if not current_page:
                return HttpResponseRedirect(reverse("test_done_page", args=[test_id]))
    else:
        current_page = Page.objects.filter(test=test, is_active=True).order_by("page_number").first()
    
    print("current page : ", current_page.page_number)
    print("per page: ", test.time_per_page)
    template = loader.get_template("test_page.html")
    context = {
        "test": current_page.test,
        "page": current_page,
        "test_page": True,
        "total_pages": total_pages,
        "total_time": total_time,
        "time_per_page": time_per_page
    }
    response = HttpResponse(template.render(context, request))
    response.set_cookie('test_id', test_id, max_age=3600, httponly=True, secure=False)
    response.set_cookie('page_id', current_page.id, max_age=3600, httponly=True, secure=False)
    response.set_cookie('page_done', 'false', max_age=3600, httponly=True, secure=False)
    response.set_cookie('is_started', 'True', max_age=3600, httponly=True, secure=False)
    return response



def start_test(request, test_id):
    test = Test.objects.filter(id=test_id, is_active=True).first()
    if not test:
        return HttpResponse("Test not found or inactive")
    total_time = test.timer_count
    
    instruction = Instruction.objects.filter(test_id=test.id).first()
    pages = Page.objects.filter(test=test, is_active=True).order_by('page_number')
    if not pages.exists():
        return HttpResponse("No pages found for this test")
    first_page = pages.first()
    template = loader.get_template("start_test.html")
    context = {
        "test": test,
        "page": first_page,
        "calculated_time": total_time,
        "instruction": instruction
    }
    response = HttpResponse(template.render(context, request))
    return response


def test_done(request, test_id):
    template = loader.get_template("test_done.html")
    test = Test.objects.filter(id=test_id).first()
    if not test:
        return HttpResponse("Test not found")
    context = {
        "test": test
    }
    return HttpResponse(template.render(context, request))



# Add setups pages
def add_test(request):
    template = loader.get_template("add_test.html")

    if request.method == "POST":
        form_data = request.POST
        name = form_data.get("name")
        page_count = form_data.get("page_count")
        timer_count = form_data.get("timer_count")
        time_per_page = form_data.get("time_per_page") == "on"
        new_test = Test(
            name=name,
            page_count=int(page_count),
            time_per_page=time_per_page,
            timer_count=int(timer_count)            
        )
        new_test.save()
        return HttpResponseRedirect(reverse("setup_tests_page"))
    context = {
    }
    response = HttpResponse(template.render(context, request))
    return response

# def add_page_to_test(request, test_id):
#     test = Test.objects.get(id=test_id)
#     template = loader.get_template("add_page.html")

#     if request == "POST":
#         form_data = request.POST
#         question = form_data.get("page_question")
#         page_number = form_data.get("page_number")
#         image = request.FILES.get("page_image")
#         new_page = Page(
#             test=test,
#             question=question,
#             page_number=page_number,
#             image=image
#             )
#         new_page.save()
#     context = {
#         "test": test,
#     }
#     response = HttpResponse(template.render(context, request))
#     return response


def add_page(request, test_id):
    template = loader.get_template("add_page.html")
    test = Test.objects.filter(id=test_id).first()
    if not test:
        return HttpResponse("Test not found")
    
    all_page_numbers = Page.objects.filter(test=test).values_list('page_number', flat=True)
    total_pages = test.page_count
    available_page_numbers = [i for i in range(1, total_pages + 1) if i not in all_page_numbers]

    if request.method == "POST":
        form_data = request.POST
        create_page(dict(form_data), test.id, request)
        return HttpResponseRedirect(reverse('setup_pages_page', args=[test.id]))
    context = {
        "test": test,
        "available_page_numbers": available_page_numbers,
    }
    response = HttpResponse(template.render(context, request))
    return response


def add_instruction(request, test_id):
    test = Test.objects.filter(id=test_id).first()
    if not test:
        return HttpResponse("Test not found")
    template = loader.get_template("add_inst.html")

    if request.method == "POST":
        form_data = request.POST
        new_instruction = Instruction(
            test = test,
            header = form_data.get("header", None),
            body = form_data.get("body", None),
            footer = form_data.get("footer", None)
        )
        new_instruction.save()
        return HttpResponseRedirect(reverse('setup_pages_page', args=[test.id]))

    context = {
        "test": test,
    }
    response = HttpResponse(template.render(context, request))
    return response

def reset_password(request, test_id):
    test = Test.objects.filter(id=test_id).first()
    
    test.password = None
    test.save()
    response =  HttpResponseRedirect(reverse("setup_pages_page", args=[test.id]))
    response.set_cookie("password_changed", "True", max_age=5, httponly=True, secure=False)
    return response


def add_password(request, test_id):
    test = Test.objects.filter(id=test_id).first()
    if not test:
        return HttpResponse("Test not found")

    template = loader.get_template("password.html")
    password_exists = test.password != None
    password_error = None
    if request.method == "POST":
        form_data = request.POST
        new_password = form_data.get('password', None)
        if password_exists:
            old_password = form_data.get('old_password', None)
            if old_password and new_password:
                if hash_string(old_password, 'md5') == test.password:
                    test.password = hash_string(new_password, 'md5')
                    test.save()
                    return HttpResponseRedirect(reverse('setup_pages_page', args=[test.id]))
                else: password_error = "Old password is incorrect"
        else:
            test.password = hash_string(new_password, 'md5')
            test.save()
            return HttpResponseRedirect(reverse('setup_pages_page', args=[test.id]))
    context = {
        "test": test,
        "password": password_exists,
        "password_error": password_error
    }
    response = HttpResponse(template.render(context, request))
    return response



def edit_instruction(request, instruct_id):
    instruction = Instruction.objects.filter(id=instruct_id).first()
    test = instruction.test
    if not instruction:
        return HttpResponse("Instruction not found")
    template = loader.get_template("add_inst.html")

    if request.method == "POST":
        form_data = request.POST
        instruction.test = test,
        instruction.header = form_data.get("header", None),
        instruction.body = form_data.get("body", None),
        instruction.footer = form_data.get("footer", None)
        instruction.save()
        return HttpResponseRedirect(reverse('setup_pages_page', args=[test.id]))

    context = {
        "test": test,
        "instruction": instruction
    }
    response = HttpResponse(template.render(context, request))
    return response


# Edit setups
def edit_test(request, test_id):
    test = Test.objects.filter(id=test_id).first()
    if not test:
        return HttpResponse("Test not found")
    template = loader.get_template("edit_test.html")

    if request.method == "POST":
        form_data = request.POST
        test.name = form_data.get("name")
        test.page_count = form_data.get("page_count")
        test.timer_count = form_data.get("timer_count")
        test.time_per_page = form_data.get("time_per_page") == "on"
        test.save()
        return HttpResponseRedirect(reverse("setup_pages_page", args=[test.id]))
    context = {
        "test": test,
    }
    response = HttpResponse(template.render(context, request))
    return response



def edit_page(request, test_id, page_id):
    page = Page.objects.filter(id=page_id).first()
    if not page:
        return HttpResponse("Page not found")
    template = loader.get_template("edit_page.html")
    test = page.test
    tests = Test.objects.filter(is_active=True)
    question_summary = get_page_question_summary(page.id)

    questions = Question.objects.filter(page=page).order_by("number")
    question_ids = questions.values_list("id", flat=True)
    images = Images.objects.filter(question_id__in=question_ids)
    sub_questions = SubQuestion.objects.filter(question_id__in=question_ids).order_by("number")


    questions_list = list(questions.values())
    images_list = list(images.values())
    sub_list = list(sub_questions.values())

    if request.method == "POST":
        form_data = request.POST
        print(form_data)
        question_ids = edit_some_page(dict(form_data), page_id, request)
        if question_ids:
            sq = Question.objects.filter(id__in=question_ids)
            if sq.count() > 0:
                sq.delete()
        return HttpResponseRedirect(reverse('setup_pages_page', args=[test.id]))
    context = {
        "page": page,
        "test": test,
        "tests": tests,
        "questions": questions,
        "sub_questions": sub_questions,
        "images": images,
        "question_summary": question_summary,
        "q_list": questions_list,
        "i_list": images_list,
        "s_list": sub_list
    }
    response = HttpResponse(template.render(context, request))
    return response



# Delete setups
def delete_test(test_id):
    test = Test.objects.filter(id=test_id).first()
    if not test:
        pass
    type = test.test_type
    test.delete()

def delete_page(page_id):
    page = Page.objects.get(id=page_id)
    page.delete()



# setups
def setup_tests(request):
    active_tests = Test.objects.filter(is_active=True)
    
    if request.method == "POST":
        form_data = request.POST
        selected = form_data.get("selected_tests")
        for s in selected:
            delete_test(s)
    inactive_tests = Test.objects.filter(is_active=False)
    template = loader.get_template("setup_tests.html")
    context = {
        "setup": True,
        "active_tests": active_tests,
        "inactive_tests": inactive_tests,
    }
    response = HttpResponse(template.render(context, request))
    return response



def setup_pages(request, test_id):
    test = Test.objects.filter(id=test_id).first()
    
    if not test:
        return HttpResponse("Test or Test type not found")
    
    password_changed = request.COOKIES.get("password_changed", None) == "True"
    active_pages = Page.objects.filter(test=test, is_active=True).order_by('page_number')
    template = loader.get_template("setup_pages.html")
    instructions = Instruction.objects.filter(test=test)
    instruction = None
    if instructions.count() > 0:
        instruction = instructions.first()
    password_exists = test.password != None
    
    if request.method == "POST":
        form_data = request.POST
        selected = form_data.get("selected_tests")
        for s in selected:
            delete_page(s)
    context = {
        "setup": True,
        "test": test,
        "active_pages": active_pages,
        "instruction": instruction,
        "password": password_exists,
        "password_changed": password_changed
    }
    response = HttpResponse(template.render(context, request))
    return response