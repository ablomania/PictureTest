from .models import *

def create_questions(form_data, request, new_page):
    question_numbers = form_data['question_number']
    questions = form_data['question']
    question_number = 1
    for question in questions:
        new_question = Question(
            number = question_number,
            page = new_page,
            text = question
        )
        new_question.save()
        #Get images
        images = request.FILES.getlist(f"page_image_{question_number}", None)
        if images:
            for image in images:
                new_image = Images(
                    image = image,
                    question = new_question
                )
                new_image.save()
        #check for and loop over sub questions
        subs = form_data.get(f'sub_{question_number}', None)
        if subs:
            sub_number = 1
            for sub in subs:
                new_sub = SubQuestion(
                    number = sub_number,
                    question = new_question,
                    text = sub
                )
                new_sub.save()
                sub_number += 1
        question_number += 1


#New Page form handler
def create_page(form_data, test_id, request):
    page_number = form_data['page_number'][0]

    #Create a new page
    new_page = Page(
        test_id = test_id,
        page_number = int(page_number)
    )
    new_page.save()
    create_questions(form_data, request, new_page)
    
    return


def edit_some_page(form_data, page_id, request):
    page = Page.objects.get(id=page_id)
    page_number = form_data['page_number'][0]

    # check for marked images and delete
    if "delete-image" in form_data:
        image_ids = form_data['delete-image']
        for image_id in image_ids:
            Images.objects.get(id=int(image_id)).delete()

    # delete all questions and sub questions related to the page
    questions = Question.objects.filter(page_id=page.id)
    question_ids = questions.values_list('id', flat=True)
    SubQuestion.objects.filter(question_id__in=question_ids).delete()
    questions.delete()

    #Create new questions and sub questions
    create_questions(form_data, request, page)
    return