from .utils import save_data, save_options, save_tagging_options, save_properties_name

# This handles the data from the options formulary and saves it to .json files.


def process_formulary(logging, data):
    use_clarifai = _process_data(logging, data)
    _process_tagging_options(logging, data, use_clarifai)
    _process_properties(logging, data)

    return data


def _process_data(logging, data):
    notion_url = data['notion_url']

    notion_token = data['notion_token']

    if data['clarifai_key']:
        clarifai_key = data['clarifai_key']
        save_data(logging, url=notion_url, token=notion_token, clarifai_key=clarifai_key)
        use_clarifai = True
    else:
        save_data(logging, url=notion_url, token=notion_token)
        use_clarifai = False

    save_options(logging, language_code=data['language_code'])

    return use_clarifai


def _process_tagging_options(logging, data, use_clarifai):
    if "delete_after_tagging" in data:
        delete_after_tagging = data['delete_after_tagging']
    else:
        delete_after_tagging = False

    confidence_treshold = 0.20

    if "confidence_treshold" in data:
        if data['confidence_treshold'] == "":
            confidence_treshold = 0.20
        else:
            confidence_treshold = data['confidence_treshold']

    logging.info(
        "Current Tagging Options --> Delete after Tagging:  {0} ,Confidence Treshold: {1} , Use Clarifai: {2}".format(
            delete_after_tagging, confidence_treshold, use_clarifai))

    save_tagging_options(logging, use_clarifai=use_clarifai, delete_after_tagging=delete_after_tagging,
                         confidence_treshold=confidence_treshold)


def _process_properties(logging, data):
    multi_tag_property = 'Tags'
    if data['multi_tag_property']:
        multi_tag_property = data['multi_tag_property']

    mind_extension_property = 'mind_extension'
    if data['mind_extension_property']:
        mind_extension_property = data['mind_extension_property']

    ai_tags_property = 'AITagsText'
    if data['ai_tags_property']:
        ai_tags_property = data['ai_tags_property']

    notion_date_property = 'reminder'
    if data['notion_date_property']:
        notion_date_property = data['notion_date_property']

    logging.info(
        "Current properties --> Multi Tag Property:  {0} , Mind extension Property: {1} , AI Tags Property: {2}, "
        "Notion Date Reminder Property: {3}".format(
            multi_tag_property, mind_extension_property, ai_tags_property, notion_date_property))

    save_properties_name(logging, multi_tag_property=multi_tag_property,
                         mind_extension_property=mind_extension_property, ai_tags_property=ai_tags_property,
                         notion_date_property=notion_date_property)
