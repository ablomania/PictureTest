from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Test, TestType, Page

# Create your views here.

def index(request):
    template = loader.get_template("index.html")

    context = {

    }
    response = HttpResponse(template.render(context, request))
    return response


def dashboard(request):
    template = loader.get_template("dashboard.html")
    active_tests = Test.objects.filter(is_active=True)

    context = {
        "active_tests": active_tests,
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
    if not current_page:
        return HttpResponse("Page not found")
    total_pages = Page.objects.filter(test=test, is_active=True).count()
    total_time = test.test_type.timer_count
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
    template = loader.get_template("test_page.html")
    context = {
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
    total_time = test.test_type.timer_count
    time_per_page = test.test_type.time_per_page
    
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
    test_type = TestType.objects.get(id=test.test_type_id)
    total_time = test_type.timer_count
    if test.test_type.unit == test_type.TimeUnit.Seconds:
        calculated_time = total_time
    elif test_type.unit == test_type.TimeUnit.Minutes:
        calculated_time = total_time / 60
        remainder = total_time % 60
        calculated_time = f"{int(calculated_time)} : {remainder}"
    else:
        remainder = total_time % 3600
        minutes = seconds = "00"
        if remainder >= 60: 
            minutes = str(int(remainder / 60))
        print("mins ", len(minutes))
        if len(minutes) == 1: minutes = f"0{minutes}"
        seconds = str(remainder % 60)
        if len(seconds) == 1: seconds = f"0{seconds}"
        calculated_time = total_time / 3600
        calculated_time = f"{int(calculated_time)} : {minutes} : {seconds}"
    
    pages = Page.objects.filter(test=test, is_active=True).order_by('page_number')
    if not pages.exists():
        return HttpResponse("No pages found for this test")
    first_page = pages.first()
    template = loader.get_template("start_test.html")
    context = {
        "test": test,
        "page": first_page,
        "calculated_time": calculated_time
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
def add_test(request, type_id):
    template = loader.get_template("add_test.html")
    type = TestType.objects.filter(id=type_id).first()
    if not type:
        return HttpResponse("Tests type not found")

    if request.method == "POST":
        form_data = request.POST
        name = form_data.get("name")
        new_test = Test(
            name=name, 
            test_type=type
        )
        new_test.save()
    context = {
        "type": type,
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


def add_page(request, type_id, test_id):
    template = loader.get_template("add_page.html")
    test = Test.objects.filter(id=test_id).first()
    if not test:
        return HttpResponse("Test not found")
    type = TestType.objects.filter(id=type_id).first()
    if not type:
        return HttpResponse("Tests type not found")
    
    all_page_numbers = Page.objects.filter(test=test).values_list('page_number', flat=True)
    total_pages = type.page_count
    available_page_numbers = [i for i in range(1, total_pages + 1) if i not in all_page_numbers]

    if request.method == "POST":
        form_data = request.POST
        print(form_data)
        question = form_data.get("page_question")
        page_number = form_data.get("page_number")
        image = request.FILES.get("page_image")
        new_page = Page(
            test=test,
            question=question,
            page_number=page_number,
            image=image
            )
        new_page.save()
        return HttpResponseRedirect(reverse('setup_pages_page', args=[type.id, test.id]))
    context = {
        "test": test,
        "type": type,
        "available_page_numbers": available_page_numbers,
    }
    response = HttpResponse(template.render(context, request))
    return response

def add_type(request):
    template = loader.get_template("add_type.html")

    if request.method == "POST":
        form_data = request.POST
        name = form_data.get("name")
        timer_count = form_data.get("timer_count")
        time_per_page = form_data.get("time_per_page") == 'on'
        page_count = form_data.get("page_count")
        description = form_data.get("description")
        unit = form_data.get("unit")
        new_type = TestType(
            name=name, 
            timer_count=timer_count,
            time_per_page=time_per_page,
            page_count=page_count,
            description=description,
            unit=unit
            )
        new_type.save()
        return HttpResponseRedirect(reverse('setup_types_page'))
    context = {

    }
    response = HttpResponse(template.render(context, request))
    return response

# Edit setups
def edit_test(request, type_id, test_id):
    test = Test.objects.filter(id=test_id).first()
    if not test:
        return HttpResponse("Test not found")
    template = loader.get_template("edit_test.html")
    type = test.test_type

    if request.method == "POST":
        form_data = request.POST
        name = form_data.get("name")
        test_type_id = form_data.get("test_type")
        test_type = TestType.objects.filter(id=test_type_id).first()
        test.name = name
        test.test_type = test_type
        test.save()
    context = {
        "test": test,
        "type": type,
    }
    response = HttpResponse(template.render(context, request))
    return response

def edit_page(request, type_id, test_id, page_id):
    page = Page.objects.filter(id=page_id).first()
    if not page:
        return HttpResponse("Page not found")
    template = loader.get_template("edit_page.html")
    current_page = Page.objects.filter(id=page_id)
    test = page.test
    type = test.test_type
    tests = Test.objects.filter(is_active=True)

    if request.method == "POST":
        form_data = request.POST
        test_id = int(form_data.get("test"))
        test = Test.objects.filter(id=test_id).first()
        question = form_data.get("page_question")
        page_number = form_data.get("page_number")
        image = request.FILES.get("page_image")
        page.test = test
        page.question = question
        page.page_number = page_number
        if image:
            page.image = image
        page.save()
        print(form_data)
        return HttpResponseRedirect(reverse('setup_pages_page', args=[type.id, test.id]))
    context = {
        "page": page,
        "test": test,
        "type": type,
        "tests": tests,
    }
    response = HttpResponse(template.render(context, request))
    return response

def edit_type(request, type_id):
    test_type = TestType.objects.get(id=type_id)
    template = loader.get_template("edit_type.html")

    if request.method == "POST":
        form_data = request.POST
        name = form_data.get("name")
        timer_count = form_data.get("timer_count")
        time_per_page = form_data.get("time_per_page") == 'on'
        page_count = form_data.get("page_count")
        description = form_data.get("description")
        unit = form_data.get("unit")
        test_type.name = name
        test_type.timer_count = timer_count
        test_type.time_per_page = time_per_page
        test_type.page_count = page_count
        test_type.description = description
        test_type.unit = unit
        test_type.save()
        return HttpResponseRedirect(reverse('setup_types_page'))
    context = {
        "test_type": test_type,
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

def delete_type(type_id):
    test_type = TestType.objects.get(id=type_id)
    test_type.delete()

# setups
def setup_tests(request, type_id):
    type = TestType.objects.filter(id=type_id).first()
    if not type:
        return HttpResponse("Tests type not found")
    active_tests = Test.objects.filter(is_active=True, test_type=type)
    
    if request.method == "POST":
        form_data = request.POST
        selected = form_data.get("selected_tests")
        for s in selected:
            delete_test(s)
    inactive_tests = Test.objects.filter(is_active=False, test_type=type)
    template = loader.get_template("setup_tests.html")
    context = {
        "setup": True,
        "active_tests": active_tests,
        "inactive_tests": inactive_tests,
        "type": type,
    }
    response = HttpResponse(template.render(context, request))
    return response

def setup_types(request):
    active_types = TestType.objects.filter(is_active=True)
    inactive_types = TestType.objects.filter(is_active=False)
    template = loader.get_template("setup_types.html")
    if request.method == "POST":
        form_data = request.POST
        print(form_data)
        selected = form_data.get("selected_tests")
        for s in selected:
            print("Hello ", s)
            delete_type(s)
    context = {
        "setup": True,
        "active_types": active_types,
        "inactive_types": inactive_types,
    }
    response = HttpResponse(template.render(context, request))
    return response

def setup_pages(request, type_id, test_id):
    test = Test.objects.filter(id=test_id).first()
    type = TestType.objects.filter(id=type_id).first()
    if not test or not type:
        return HttpResponse("Test or Test type not found")
    active_pages = Page.objects.filter(test=test, is_active=True).order_by('page_number')
    template = loader.get_template("setup_pages.html")
    
    if request.method == "POST":
        form_data = request.POST
        selected = form_data.get("selected_tests")
        for s in selected:
            delete_page(s)
    context = {
        "setup": True,
        "test": test,
        "active_pages": active_pages,
        "type": type,
    }
    response = HttpResponse(template.render(context, request))
    return response