from django import template
from django.shortcuts import get_object_or_404
from odpro.models import MCQuestion, Category, SubCategory

register = template.Library()

@register.inclusion_tag('odpro/subcategory_list.html', takes_context=True)
def subcategories_list_for_category(context, category):
    mylist = []
    subcat_list = list(SubCategory.objects.filter(category=category.id).order_by('sub_category'))
    for s in subcat_list:
        name = s.subcategory_name()
        mylist.append(name)
    return {'subcat_list': mylist}

@register.inclusion_tag('odpro/correct_answer.html', takes_context=True)
def correct_answer_for_all(context, question):
    """
    INCLUSION TAGS DISPLAY DATA BY RENDERING ANOTHER TEMPLATE
    RETURNS A DICTIONARY
    TAKES_CONTEXT: THE TAG WILL HAVE NO REQUIRED ARGUMENTS; THE FUNCTION WILL HAVE ONE (CONTEXT)
    processes the correct answer based on a given question object
    if the answer is incorrect, informs the user
    """
    answers = question.get_answers()
    incorrect_list = context.get('incorrect_questions', [])
    if question.id in incorrect_list:
        user_was_incorrect = True
    else:
        user_was_incorrect = False

    return {'previous': {'answers': answers},
            'user_was_incorrect': user_was_incorrect}


@register.filter
def answer_choice_to_string(question, answer):
    return question.answer_choice_to_string(answer)
