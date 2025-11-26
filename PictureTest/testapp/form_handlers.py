from .models import *

def create_questions(form_data, request, new_page):
    questions = form_data['question']
    question_objs = []
    question_map = {}  # map index to Question for later use
    for idx, question in enumerate(questions, start=1):
        if question != "":
            q_obj = Question(number=idx, page=new_page, text=question)
            question_objs.append(q_obj)
            question_map[idx] = q_obj
    Question.objects.bulk_create(question_objs)

    # Refresh from DB to get IDs
    created_questions = list(Question.objects.filter(page=new_page).order_by('number'))
    # Map by number for image/sub assignment
    qnum_to_obj = {q.number: q for q in created_questions}

    image_objs = []
    sub_objs = []
    for idx, question in enumerate(questions, start=1):
        if question != "":
            q_obj = qnum_to_obj.get(idx)
            # Images
            images = request.FILES.getlist(f"page_image_{idx}", None)
            if images:
                for image in images:
                    image_objs.append(Images(image=image, question=q_obj))
            # SubQuestions
            subs = form_data.get(f'sub_{idx}', None)
            if subs:
                for sub_idx, sub in enumerate(subs, start=1):
                    if sub != "":
                        sub_objs.append(SubQuestion(number=sub_idx, question=q_obj, text=sub))
    if image_objs:
        Images.objects.bulk_create(image_objs)
    if sub_objs:
        SubQuestion.objects.bulk_create(sub_objs)


#New Page form handler
def create_page(form_data, test_id, request):
    page_number = int(form_data['page_number'][0])
    new_page = Page(test_id=test_id, page_number=page_number)
    new_page.save()
    create_questions(form_data, request, new_page)
    # No need to return anything


def edit_some_page(form_data, page_id, request):
    page = Page.objects.get(id=page_id)
    # Update page number if changed
    new_page_number = int(form_data['page_number'][0])
    if page.page_number != new_page_number:
        page.page_number = new_page_number
        page.save(update_fields=['page_number'])

    # Bulk delete marked images
    if "delete-image" in form_data:
        image_ids = [int(i) for i in form_data['delete-image']]
        print("image_ids : ", image_ids)
        Images.objects.filter(id__in=image_ids).delete()

    # Bulk delete all questions and sub questions related to the page
    old_questions = Question.objects.filter(page_id=page.id).order_by("number")
    question_ids = list(old_questions.values_list('id', flat=True))
    old_subs = SubQuestion.objects.filter(question_id__in=question_ids).order_by("number")

    # Bulk create new questions
    new_questions = form_data['question']
    new_list = []
    count = 1
    for q in new_questions:
        if q != "":
            new_question = Question(
                text = q,
                number = count,
                page = page
            )
            new_question.save()
            # Get images
            images = request.FILES.getlist(f"page_image_{count}", None)
            if images:
                for image in images:
                    new_image = Images(
                        image = image,
                        question = new_question
                    )
                    new_image.save()
            subs = form_data.get(f'sub_{count}', None)
            if subs:
                sub_number = 1
                for sub in subs:
                    if sub != "":
                        new_sub = SubQuestion(
                            number = sub_number,
                            question = new_question,
                            text = sub
                        )
                        new_sub.save()
                        sub_number += 1
            new_list.append(new_question)
            count += 1

    related_images = Images.objects.filter(question_id__in=question_ids)
    print("related ", related_images)
    for i in related_images:
        qn = i.question.number
        new_question = next((obj for obj in new_list if obj.number == qn), None)
        if new_question:
            i.question = new_question
            i.save()
            print("Updated image ", i.id, " to question ", new_question.id)

    return question_ids


def delete_pages(page_ids):
        # convert to list of integers
        page_ids = [int(pid) for pid in page_ids]
        pages = Page.objects.filter(id__in=page_ids)
        for page in pages:
            page.is_active = False
        Page.objects.bulk_update(pages, ['is_active'])


def delete_tests(test_ids):
    # convert to list of integers
    test_ids = [int(tid) for tid in test_ids]
    tests = Test.objects.filter(id__in=test_ids)
    for test in tests:
        test.is_active = False
    Test.objects.bulk_update(tests, ['is_active'])